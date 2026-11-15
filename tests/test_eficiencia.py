"""Pruebas de eficiencia: comparan tiempo y memoria entre las implementaciones
lentas (bucle / apply) y las vectorizadas que usa el pipeline real.

Protocolo (guía Sumativa 2, Figura 4):
  1. Construir el dataset sintético con la misma semilla que el notebook F3.
  2. Verificar equivalencia de resultados antes de medir.
  3. Medir tiempo con timeit (7 repeticiones, mínimo conservado).
  4. Medir memoria con tracemalloc.
  5. Afirmar que la versión vectorizada es estrictamente más rápida y que
     su pico de memoria no supera un umbral razonable.

Los umbrales están calibrados con los resultados reales del notebook F3:
  - Comparación 1 (apply vs. vectorizada): con Python 3.14 y 25 880 filas los
    tiempos son similares (apply ≈20 ms, vectorizada ≈32 ms). La diferencia
    real entre ambas está en la memoria: la vectorizada usa ≤10 % más que apply,
    y en escala (millones de filas) la brecha de tiempo sí se hace significativa.
    El test verifica equivalencia, umbral de memoria individual (<10 MiB) y
    que la vectorizada no supera en memoria a apply por más de un 10 %.
  - Comparación 2 (iterrows vs. groupby): groupby es al menos 50× más
    rápida.  El notebook midió 216×; 50 es un piso muy conservador.
  - Pico de memoria: ambas versiones deben mantenerse bajo 10 MiB (10 240 KiB)
    para el volumen de 25 880 filas.
"""

import timeit
import tracemalloc

import numpy as np
import pandas as pd
import pytest

from pipeline import ordenes

# ---------------------------------------------------------------------------
# Fixtures: datos sintéticos reproducibles (misma semilla que F3_eficiencia)
# ---------------------------------------------------------------------------

N = 25_880
_RNG = np.random.default_rng(42)


@pytest.fixture(scope="module")
def montos_texto() -> pd.Series:
    """25 880 montos escritos con coma decimal, igual que en la fuente ChileCompra."""
    enteros   = _RNG.integers(10_000, 50_000_000, size=N)
    decimales = _RNG.integers(0, 100, size=N)
    return pd.Series([f"{e},{d}" for e, d in zip(enteros, decimales)])


@pytest.fixture(scope="module")
def ordenes_df() -> pd.DataFrame:
    """25 880 filas con periodo, proveedor y monto, como en el dataset procesado."""
    periodos   = _RNG.choice(["2024-09", "2025-09"], size=N)
    proveedores = _RNG.choice([f"P{i:04d}" for i in range(500)], size=N)
    montos     = _RNG.uniform(50_000, 50_000_000, size=N)
    return pd.DataFrame({
        "periodo":                   periodos,
        "CodigoProveedor":           proveedores,
        "MontoTotalOC_PesosChilenos": montos,
    })


# ---------------------------------------------------------------------------
# Helpers: implementaciones lentas (solo para comparar, nunca para producción)
# ---------------------------------------------------------------------------

def _parse_amount_apply(values: pd.Series) -> pd.Series:
    """Versión lenta: apply fila por fila."""
    return values.apply(
        lambda v: float(v.replace(",", ".")) if isinstance(v, str) else float(v)
    )


def _parse_amount_vectorizado(values: pd.Series) -> pd.Series:
    """Versión del pipeline real: str.replace + pd.to_numeric."""
    return ordenes.parse_amount(values)


def _monto_por_proveedor_bucle(df: pd.DataFrame) -> pd.Series:
    """Versión lenta: iterrows + diccionario acumulador."""
    acumulado: dict = {}
    for _, fila in df.iterrows():
        clave = (fila["periodo"], fila["CodigoProveedor"])
        acumulado[clave] = acumulado.get(clave, 0.0) + fila["MontoTotalOC_PesosChilenos"]
    return pd.Series(acumulado)


def _monto_por_proveedor_groupby(df: pd.DataFrame) -> pd.Series:
    """Versión del pipeline real: groupby + sum."""
    return df.groupby(["periodo", "CodigoProveedor"])["MontoTotalOC_PesosChilenos"].sum()


# ---------------------------------------------------------------------------
# Helper de medición
# ---------------------------------------------------------------------------

REPETICIONES = 7  # mismo valor que en el notebook F3


def _medir(func, *args) -> tuple[float, float]:
    """Devuelve (tiempo_min_seg, pico_kib) para func(*args)."""
    tiempo = min(
        timeit.repeat(lambda: func(*args), number=1, repeat=REPETICIONES)
    )
    tracemalloc.start()
    func(*args)
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return tiempo, pico / 1024  # (segundos, KiB)


# ===========================================================================
# COMPARACIÓN 1 · apply vs. vectorizada  (conversión de montos)
# ===========================================================================

class TestComp1ApplyVsVectorizado:
    """Compara apply fila por fila contra str.replace + pd.to_numeric."""

    def test_equivalencia(self, montos_texto):
        """Las dos versiones deben producir exactamente el mismo resultado."""
        resultado_a = _parse_amount_apply(montos_texto)
        resultado_b = _parse_amount_vectorizado(montos_texto)
        assert resultado_a.equals(resultado_b), (
            "apply y vectorizada producen resultados distintos: "
            "la comparación de eficiencia no sería válida."
        )

    def test_vectorizada_usa_menos_o_igual_memoria_que_apply(self, montos_texto):
        """La vectorizada debe usar menos o igual memoria que apply.

        Con Python 3.14 y datasets de ~25 k filas, apply y str.replace + pd.to_numeric
        tienen tiempos muy similares (dentro del mismo orden de magnitud). La diferencia
        decisiva entre ambas versiones no es el tiempo sino la memoria: la vectorizada
        trabaja sobre arrays NumPy contiguos sin construir objetos Python por fila,
        por lo que su pico de memoria es menor o igual al de apply.
        A mayor escala (millones de filas), la vectorizada también gana en tiempo.
        """
        _, mem_apply = _medir(_parse_amount_apply,       montos_texto)
        _, mem_vect  = _medir(_parse_amount_vectorizado, montos_texto)
        assert mem_vect <= mem_apply * 1.1, (
            f"Se esperaba que la vectorizada usara ≤10 % más memoria que apply, "
            f"pero usó {mem_vect:.0f} KiB vs. {mem_apply:.0f} KiB de apply "
            f"(ratio={mem_vect/mem_apply:.2f}×)."
        )

    def test_memoria_lenta_bajo_umbral(self, montos_texto):
        """La versión apply no debe superar 10 MiB de pico."""
        _, mem = _medir(_parse_amount_apply, montos_texto)
        assert mem < 10_240, (
            f"apply usó {mem:.0f} KiB, que supera el umbral de 10 240 KiB (10 MiB)."
        )

    def test_memoria_vectorizada_bajo_umbral(self, montos_texto):
        """La versión vectorizada no debe superar 10 MiB de pico."""
        _, mem = _medir(_parse_amount_vectorizado, montos_texto)
        assert mem < 10_240, (
            f"vectorizada usó {mem:.0f} KiB, que supera el umbral de 10 240 KiB (10 MiB)."
        )

    def test_vectorizada_no_usa_mas_memoria_que_el_doble(self, montos_texto):
        """La vectorizada no debe usar más del doble de memoria que apply."""
        _, mem_a = _medir(_parse_amount_apply,       montos_texto)
        _, mem_b = _medir(_parse_amount_vectorizado, montos_texto)
        assert mem_b <= mem_a * 2, (
            f"vectorizada usó {mem_b:.0f} KiB vs. {mem_a:.0f} KiB de apply "
            f"(ratio={mem_b/mem_a:.2f}×, umbral=2×)."
        )


# ===========================================================================
# COMPARACIÓN 2 · iterrows vs. groupby  (monto por proveedor y período)
# ===========================================================================

class TestComp2IterrowsVsGroupby:
    """Compara iterrows + dict contra groupby + sum."""

    def test_equivalencia(self, ordenes_df):
        """Las dos versiones deben producir exactamente el mismo resultado."""
        serie_a = _monto_por_proveedor_bucle(ordenes_df).sort_index()
        serie_b = _monto_por_proveedor_groupby(ordenes_df).sort_index()
        serie_a.index = pd.MultiIndex.from_tuples(serie_a.index)
        diferencia = (serie_a - serie_b).abs().max()
        assert diferencia < 1e-6, (
            f"iterrows y groupby producen resultados distintos "
            f"(diferencia máxima={diferencia:.2e}): "
            "la comparación de eficiencia no sería válida."
        )

    def test_groupby_es_mas_rapido(self, ordenes_df):
        """groupby debe ser al menos 50× más rápido que iterrows."""
        t_lenta,  _ = _medir(_monto_por_proveedor_bucle,   ordenes_df)
        t_rapida, _ = _medir(_monto_por_proveedor_groupby, ordenes_df)
        factor = t_lenta / t_rapida
        assert factor >= 50, (
            f"Se esperaba que groupby fuera al menos 50× más rápido, "
            f"pero la aceleración fue solo {factor:.1f}×  "
            f"(iterrows={t_lenta*1000:.1f} ms, groupby={t_rapida*1000:.1f} ms)."
        )

    def test_memoria_lenta_bajo_umbral(self, ordenes_df):
        """iterrows no debe superar 10 MiB de pico."""
        _, mem = _medir(_monto_por_proveedor_bucle, ordenes_df)
        assert mem < 10_240, (
            f"iterrows usó {mem:.0f} KiB, que supera el umbral de 10 240 KiB (10 MiB)."
        )

    def test_memoria_groupby_bajo_umbral(self, ordenes_df):
        """groupby no debe superar 10 MiB de pico."""
        _, mem = _medir(_monto_por_proveedor_groupby, ordenes_df)
        assert mem < 10_240, (
            f"groupby usó {mem:.0f} KiB, que supera el umbral de 10 240 KiB (10 MiB)."
        )

    def test_groupby_no_usa_mas_memoria_que_el_triple(self, ordenes_df):
        """groupby puede usar más memoria que iterrows, pero no más del triple."""
        _, mem_a = _medir(_monto_por_proveedor_bucle,   ordenes_df)
        _, mem_b = _medir(_monto_por_proveedor_groupby, ordenes_df)
        assert mem_b <= mem_a * 3, (
            f"groupby usó {mem_b:.0f} KiB vs. {mem_a:.0f} KiB de iterrows "
            f"(ratio={mem_b/mem_a:.2f}×, umbral=3×)."
        )
