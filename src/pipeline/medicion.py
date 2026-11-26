"""Utilidades de medición de eficiencia para el proyecto ABP.

Centraliza las funciones de benchmark (tiempo y memoria) y las
implementaciones de comparación (versión lenta vs. versión del pipeline)
para que el notebook F3 y los tests de eficiencia usen exactamente el
mismo código, sin duplicarlo.

Uso típico:
    from pipeline.medicion import (
        medir,
        parse_amount_apply,
        parse_amount_vectorizado,
        monto_por_proveedor_bucle,
        monto_por_proveedor_groupby,
        classify_modality_apply,
        classify_modality_select,
        REPETICIONES,
    )
"""

from __future__ import annotations

import timeit
import tracemalloc
from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd

from . import ordenes

# ---------------------------------------------------------------------------
# Parámetro de benchmark
# ---------------------------------------------------------------------------

REPETICIONES = 7  # timeit.repeat: medir N veces y conservar el mínimo


# ---------------------------------------------------------------------------
# Medidor genérico
# ---------------------------------------------------------------------------

def medir(func: Callable[..., Any], *args: Any) -> tuple[float, float]:
    """Ejecuta func(*args), mide tiempo y memoria y devuelve (segundos, KiB).

    Protocolo (guía Sumativa 2, Figura 4):
      - Tiempo: timeit.repeat con REPETICIONES repeticiones, se conserva el mínimo.
      - Memoria: pico reportado por tracemalloc en una sola ejecución.
    """
    tiempo = min(timeit.repeat(lambda: func(*args), number=1, repeat=REPETICIONES))

    tracemalloc.start()
    func(*args)
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return tiempo, pico / 1024  # (segundos, KiB)


# ---------------------------------------------------------------------------
# Comparación 1 · conversión de montos con coma decimal
# ---------------------------------------------------------------------------

def parse_amount_apply(values: pd.Series) -> pd.Series:
    """Versión de referencia: recorre cada celda con apply.

    Con cadenas de texto Python (sin pyarrow), el trabajo por celda es
    idéntico en las dos versiones: el intérprete llama a str.replace y
    float() tanto en el lambda como en la ruta interna de pd.to_numeric.
    Por eso apply no es más lenta que la versión vectorizada; incluso puede
    ser ligeramente más rápida al evitar la serie intermedia.
    Solo para comparar. El pipeline real usa parse_amount_vectorizado.
    """
    return values.apply(
        lambda v: float(v.replace(",", ".")) if isinstance(v, str) else float(v)
    )


def parse_amount_vectorizado(values: pd.Series) -> pd.Series:
    """Versión del pipeline real: str.replace + pd.to_numeric.

    Con Series de cadenas Python (no pyarrow), el rendimiento es similar al
    de apply: ambas rutas procesan celda por celda en el intérprete.
    La ventaja de la vectorización aparece en operaciones numéricas puras
    (Comparación 2 y 3), no en manipulación de strings.
    """
    return ordenes.parse_amount(values)


# ---------------------------------------------------------------------------
# Comparación 2 · monto total por proveedor y período
# ---------------------------------------------------------------------------

def monto_por_proveedor_bucle(df: pd.DataFrame) -> pd.Series:
    """Versión lenta: recorre cada fila con iterrows y acumula en un dict.

    iterrows convierte cada fila en un objeto Series de Python antes de
    entregarla al bucle: una asignación de memoria por fila.
    Esta comparación solo evalúa este bucle frente a groupby.
    Solo para comparar. El pipeline real usa monto_por_proveedor_groupby.
    """
    acumulado: dict = {}
    for _, fila in df.iterrows():
        clave = (fila["periodo"], fila["CodigoProveedor"])
        acumulado[clave] = acumulado.get(clave, 0.0) + fila["MontoTotalOC_PesosChilenos"]
    return pd.Series(acumulado)


def monto_por_proveedor_groupby(df: pd.DataFrame) -> pd.Series:
    """Versión del pipeline real: groupby + sum.

    Agrupa por columnas sin construir una Series de Python por cada fila.
    Los factores de tiempo y memoria se informan con las mediciones ejecutadas,
    no como propiedades constantes de esta implementación.
    """
    return df.groupby(["periodo", "CodigoProveedor"])["MontoTotalOC_PesosChilenos"].sum()


# ---------------------------------------------------------------------------
# Comparación 3 · clasificación de modalidad
# ---------------------------------------------------------------------------

_MODALITIES = ("Compra ágil", "Trato directo", "Convenio marco", "Licitación", "Otra")


def classify_modality_apply(df: pd.DataFrame) -> pd.Series:
    """Versión lenta: aplica la lógica fila por fila con apply.

    Construye un objeto Python por fila para evaluar las condiciones.
    Solo para comparar. El pipeline real usa classify_modality_select.
    """
    def _classify(row):
        if row.get("EsCompraAgil") is True:
            return _MODALITIES[0]
        if row.get("EsTratoDirecto") is True:
            return _MODALITIES[1]
        if row.get("Tipo") == "CM":
            return _MODALITIES[2]
        if pd.notna(row.get("CodigoLicitacion")):
            return _MODALITIES[3]
        return _MODALITIES[4]

    return df.apply(_classify, axis=1)


def classify_modality_select(df: pd.DataFrame) -> pd.Series:
    """Versión del pipeline real: np.select sobre arrays booleanos.

    Evalúa las cuatro condiciones como máscaras NumPy sobre columnas completas
    y elige el resultado con np.select, sin construir objetos Python por fila.
    La ventaja de tiempo y memoria depende de los datos y del entorno de ejecución;
    se cuantifica en los notebooks de eficiencia.
    """
    conditions = [
        df["EsCompraAgil"].fillna(False).astype(bool),
        df["EsTratoDirecto"].fillna(False).astype(bool),
        df["Tipo"].eq("CM").fillna(False),
        df["CodigoLicitacion"].notna(),
    ]
    return pd.Series(
        np.select(conditions, _MODALITIES[:4], default=_MODALITIES[4]),
        index=df.index,
    )
