"""Pruebas de la medición de eficiencia.

No se afirma ningún tiempo: dependen de la máquina. Se prueba lo que sí es estable:
que las versiones fila por fila dan lo mismo que las del pipeline y que la tabla de
resultados tiene la forma esperada.
"""

import pandas as pd
import pytest

from pipeline import medicion


@pytest.mark.parametrize("position", range(6))
def test_las_versiones_fila_por_fila_dan_lo_mismo_que_el_pipeline(synthetic_lines, position):
    case = medicion.build_cases(synthetic_lines)[position]
    expected = case["pipeline"][1](*case["args"])
    for _, slow in case["row_wise"]:
        case["same"](slow(*case["args"]), expected)


def test_las_versiones_no_modifican_la_entrada(synthetic_lines):
    for case in medicion.build_cases(synthetic_lines):
        copies = [arg.copy(deep=True) if hasattr(arg, "copy") else arg for arg in case["args"]]
        for _, function in [case["pipeline"], *case["row_wise"]]:
            function(*case["args"])
        for arg, copy in zip(case["args"], copies):
            if isinstance(arg, pd.DataFrame):
                pd.testing.assert_frame_equal(arg, copy)
            elif isinstance(arg, pd.Series):
                pd.testing.assert_series_equal(arg, copy)


def test_measure_devuelve_tiempo_y_memoria_positivos():
    ms, mib = medicion.measure(lambda: [0] * 100_000, repeats=2)
    assert ms > 0 and mib > 0


def test_compare_entrega_una_fila_por_version(synthetic_lines):
    table = medicion.compare(synthetic_lines, repeats=1)
    assert list(table.columns) == ["operacion", "version", "en_pipeline", "filas", "tiempo_ms", "memoria_mib", "aceleracion"]
    assert table["operacion"].nunique() == 6
    assert table["en_pipeline"].sum() == 6  # una versión del pipeline por operación
    assert (table.loc[table["en_pipeline"], "aceleracion"] == 1).all()
    assert (table["tiempo_ms"] > 0).all()


def test_compare_falla_si_una_version_da_otro_resultado(synthetic_lines, monkeypatch):
    monkeypatch.setattr(medicion, "parse_amount_apply", lambda values: values.str.len().astype(float))
    with pytest.raises(AssertionError):
        medicion.compare(synthetic_lines, repeats=1)


def test_compare_omite_las_versiones_indicadas(synthetic_lines):
    table = medicion.compare(synthetic_lines, repeats=1, skip=("iterrows",))
    assert "iterrows" not in set(table["version"])
    assert "itertuples" in set(table["version"])
