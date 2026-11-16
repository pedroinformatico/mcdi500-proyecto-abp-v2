"""Medición de eficiencia: cada operación del pipeline contra una versión fila por fila.

Protocolo de la guía de la Fase 3: elegir una operación real, escribir dos versiones,
comprobar que dan el mismo resultado y recién entonces medir tiempo (`timeit`, se
conserva el mínimo) y memoria máxima (`tracemalloc`).

Las versiones fila por fila de este módulo existen solo para comparar: el pipeline
nunca las usa. `compare(lines)` recorre todas las operaciones y devuelve una tabla.
"""

from __future__ import annotations

import timeit
import tracemalloc
from collections.abc import Callable

import numpy as np
import pandas as pd

from . import ordenes
from .flujo import build_orders_pipeline

REPEATS = 7  # repeticiones por medición; se conserva la más rápida
SLOW_SECONDS = 2.0  # una versión que tarda más que esto se repite menos
SLOW_REPEATS = 3

AMOUNT = ordenes.AMOUNT_COLUMN
SUPPLIER_KEYS = ["periodo", "CodigoProveedor"]


# --- Versiones fila por fila (solo para comparar) ---


def parse_amount_apply(values: pd.Series) -> pd.Series:
    """Convierte los montos celda por celda con `apply`."""
    return values.apply(lambda value: float(value.replace(",", ".")) if isinstance(value, str) else np.nan)


def classify_modality_apply(orders: pd.DataFrame) -> pd.DataFrame:
    """Clasifica la modalidad fila por fila, con las mismas reglas y en el mismo orden."""

    def label(row: pd.Series) -> str:
        if row["EsCompraAgil"] is True:
            return ordenes.MODALITIES[0]
        if row["EsTratoDirecto"] is True:
            return ordenes.MODALITIES[1]
        if row["Tipo"] == "CM":
            return ordenes.MODALITIES[2]
        if pd.notna(row["CodigoLicitacion"]):
            return ordenes.MODALITIES[3]
        return ordenes.MODALITIES[4]

    labeled = orders.copy()
    labeled["modalidad"] = orders.apply(label, axis=1)
    return labeled


def aggregate_orders_loop(lines: pd.DataFrame) -> pd.DataFrame:
    """Deja una fila por orden recorriendo las líneas y acumulando en un diccionario."""
    columns = list(ordenes.ORDER_COLUMNS)
    first: dict[str, list] = {}
    count: dict[str, int] = {}
    for row in lines[["Codigo", *columns]].itertuples(index=False):
        code = row[0]
        if code not in first:
            first[code] = list(row[1:])
            count[code] = 1
            continue
        count[code] += 1
        kept = first[code]
        for position, value in enumerate(row[1:]):  # igual que groupby.first: el primer valor no nulo
            if pd.isna(kept[position]) and not pd.isna(value):
                kept[position] = value
    orders = pd.DataFrame(list(first.values()), columns=columns)
    orders["lineas"] = list(count.values())
    return orders


def supplier_amount_iterrows(orders: pd.DataFrame) -> pd.Series:
    """Suma el monto por período y proveedor con `iterrows`, la forma más lenta de recorrer."""
    total: dict[tuple, float] = {}
    for _, row in orders.iterrows():
        key = (row["periodo"], row["CodigoProveedor"])
        total[key] = total.get(key, 0.0) + row[AMOUNT]
    return _supplier_series(total)


def supplier_amount_itertuples(orders: pd.DataFrame) -> pd.Series:
    """Suma el monto por período y proveedor con `itertuples`: un bucle escrito con cuidado."""
    total: dict[tuple, float] = {}
    for period, supplier, amount in orders[[*SUPPLIER_KEYS, AMOUNT]].itertuples(index=False):
        total[(period, supplier)] = total.get((period, supplier), 0.0) + amount
    return _supplier_series(total)


def flag_extreme_amounts_loop(orders: pd.DataFrame, limit: float) -> pd.DataFrame:
    """Marca las órdenes extremas comparando monto por monto."""
    flagged = orders.copy()
    flagged[ordenes.EXTREME_COLUMN] = [amount > limit for amount in orders[AMOUNT]]
    return flagged


# --- Versiones del pipeline que no son una sola función de ordenes.py ---


def supplier_amount_groupby(orders: pd.DataFrame) -> pd.Series:
    """Monto por período y proveedor, como lo calcula `ordenes.top_supplier_share`."""
    return orders.groupby(SUPPLIER_KEYS)[AMOUNT].sum()


def run_functions(lines: pd.DataFrame) -> pd.DataFrame:
    """El pipeline como funciones encadenadas (Fase 2)."""
    typed = ordenes.cast_types(ordenes.normalize_missing(lines))
    return ordenes.flag_extreme_amounts(ordenes.aggregate_orders(ordenes.classify_modality(typed)))


def run_classes(lines: pd.DataFrame) -> pd.DataFrame:
    """El pipeline como clases (Fase 3)."""
    return build_orders_pipeline().fit_transform(lines)


# --- Medición ---


def measure(function: Callable, *args, repeats: int = REPEATS) -> tuple[float, float]:
    """Devuelve (milisegundos, MiB): el menor tiempo de varias repeticiones y la memoria máxima.

    El tiempo y la memoria se miden en llamadas separadas, porque `tracemalloc` vuelve
    más lento el código que observa.
    """
    first = timeit.timeit(lambda: function(*args), number=1)
    if first > SLOW_SECONDS:
        repeats = min(repeats, SLOW_REPEATS)
    times = [first, *timeit.repeat(lambda: function(*args), number=1, repeat=max(repeats - 1, 0))]
    tracemalloc.start()
    try:
        function(*args)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return min(times) * 1000, peak / 2**20


def build_cases(lines: pd.DataFrame) -> list[dict]:
    """Prepara la entrada de cada operación y sus dos (o tres) versiones.

    Cada caso trae la versión del pipeline, las versiones fila por fila y la función
    que comprueba que dos resultados son iguales.
    """
    clean = ordenes.normalize_missing(lines)
    typed = ordenes.cast_types(clean)
    labeled = ordenes.classify_modality(typed)
    orders = ordenes.aggregate_orders(labeled)
    limit = ordenes.extreme_amount_limit(orders[AMOUNT])
    return [
        {
            "operation": "Convertir montos",
            "args": (clean[AMOUNT],),
            "pipeline": ("str.replace + to_numeric", ordenes.parse_amount),
            "row_wise": [("apply", parse_amount_apply)],
            "same": pd.testing.assert_series_equal,
        },
        {
            "operation": "Clasificar modalidad",
            "args": (typed,),
            "pipeline": ("np.select", ordenes.classify_modality),
            "row_wise": [("apply por fila", classify_modality_apply)],
            "same": _assert_same_frame,
        },
        {
            "operation": "Una fila por orden",
            "args": (labeled,),
            "pipeline": ("groupby.first", ordenes.aggregate_orders),
            "row_wise": [("bucle con itertuples", aggregate_orders_loop)],
            "same": _assert_same_frame,
        },
        {
            "operation": "Monto por proveedor",
            "args": (orders,),
            "pipeline": ("groupby.sum", supplier_amount_groupby),
            "row_wise": [("iterrows", supplier_amount_iterrows), ("itertuples", supplier_amount_itertuples)],
            "same": _assert_same_amounts,
        },
        {
            "operation": "Marcar montos extremos",
            "args": (orders, limit),
            "pipeline": ("comparación vectorial", ordenes.flag_extreme_amounts),
            "row_wise": [("lista por comprensión", flag_extreme_amounts_loop)],
            "same": _assert_same_frame,
        },
        {
            "operation": "Pipeline completo",
            "args": (lines,),
            "pipeline": ("clases (Fase 3)", run_classes),
            "row_wise": [("funciones encadenadas (Fase 2)", run_functions)],
            "same": _assert_same_frame,
        },
    ]


def compare(lines: pd.DataFrame, repeats: int = REPEATS, skip: tuple[str, ...] = ()) -> pd.DataFrame:
    """Mide todas las operaciones sobre `lines` y devuelve una fila por versión.

    Antes de medir comprueba que cada versión fila por fila da lo mismo que la del
    pipeline: si no, lanza AssertionError, porque comparar tiempos no tendría sentido.
    'aceleracion' dice cuántas veces más rápida es la versión del pipeline que esa fila.
    `skip` lista versiones fila por fila que no se ejecutan (por ejemplo "iterrows" con
    mucho volumen).
    """
    rows = []
    for case in build_cases(lines):
        case["row_wise"] = [(slow_name, slow) for slow_name, slow in case["row_wise"] if slow_name not in skip]
        name, function = case["pipeline"]
        expected = function(*case["args"])
        for _, slow in case["row_wise"]:
            case["same"](slow(*case["args"]), expected)
        pipeline_ms, pipeline_mib = measure(function, *case["args"], repeats=repeats)
        for slow_name, slow in case["row_wise"]:
            ms, mib = measure(slow, *case["args"], repeats=repeats)
            rows.append(_row(case, slow_name, False, ms, mib, ms / pipeline_ms))
        rows.append(_row(case, name, True, pipeline_ms, pipeline_mib, 1.0))
    return pd.DataFrame(rows)


def _row(case: dict, version: str, in_pipeline: bool, ms: float, mib: float, speedup: float) -> dict:
    return {
        "operacion": case["operation"],
        "version": version,
        "en_pipeline": in_pipeline,
        "filas": len(case["args"][0]),
        "tiempo_ms": round(ms, 2),
        "memoria_mib": round(mib, 2),
        "aceleracion": round(speedup, 2),
    }


def _supplier_series(total: dict[tuple, float]) -> pd.Series:
    index = pd.MultiIndex.from_tuples(list(total), names=SUPPLIER_KEYS)
    return pd.Series(list(total.values()), index=index, name=AMOUNT)


def _assert_same_frame(result: pd.DataFrame, expected: pd.DataFrame) -> None:
    pd.testing.assert_frame_equal(result, expected, check_dtype=False)


def _assert_same_amounts(result: pd.Series, expected: pd.Series) -> None:
    # La suma en otro orden cambia los últimos decimales: se compara con tolerancia.
    pd.testing.assert_series_equal(result.sort_index(), expected.sort_index(), rtol=1e-9)
