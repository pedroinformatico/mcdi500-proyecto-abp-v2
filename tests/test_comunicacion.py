"""Verificación de las tablas y figuras que alimentan la comunicación de F4."""

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from pipeline import comunicacion, ordenes


@pytest.fixture(scope="module")
def orders(synthetic_lines):
    typed = ordenes.cast_types(ordenes.normalize_missing(synthetic_lines))
    result = ordenes.aggregate_orders(ordenes.classify_modality(typed))
    return ordenes.flag_extreme_amounts(result)


def test_modality_table_conserves_totals_and_period_denominators(orders):
    table = comunicacion.modality_table(orders)
    assert len(table) == 2 * len(ordenes.MODALITIES)
    for period, group in table.groupby("periodo"):
        source = orders[orders["periodo"] == period]
        assert group["ordenes"].sum() == len(source)
        assert group["monto_pesos"].sum() == pytest.approx(source[ordenes.AMOUNT_COLUMN].sum())
        assert group["porcentaje_ordenes"].sum() == pytest.approx(100)
        assert group["porcentaje_monto"].sum() == pytest.approx(100)


def test_extreme_summary_uses_existing_flags(orders):
    summary = comunicacion.extreme_summary(orders)
    marked = orders["monto_extremo"]
    assert summary["extremas"] == int(marked.sum())
    assert summary["porcentaje_monto"] == pytest.approx(
        orders.loc[marked, ordenes.AMOUNT_COLUMN].sum() / orders[ordenes.AMOUNT_COLUMN].sum() * 100
    )
    histogram = comunicacion.extreme_histogram_table(orders)
    assert histogram["ordenes"].sum() == (orders[ordenes.AMOUNT_COLUMN] > 0).sum()


def test_concentration_is_monotone_and_sensitive_to_extremes(orders):
    table = comunicacion.concentration_table(orders)
    assert set(table["escenario"]) == {"Todas", "Sin extremas"}
    for (period, scenario), group in table.groupby(["periodo", "escenario"]):
        assert group["participacion_acumulada_pct"].between(0, 100).all()
        assert group["participacion_acumulada_pct"].is_monotonic_increasing
        source = orders[orders["periodo"] == period]
        if scenario == "Sin extremas":
            source = source[~source["monto_extremo"]]
        amounts = source.groupby("CodigoProveedor")[ordenes.AMOUNT_COLUMN].sum()
        expected = amounts.nlargest(10).sum() / amounts.sum() * 100
        assert group.iloc[-1]["participacion_acumulada_pct"] == pytest.approx(expected)


def test_dependence_and_findings_share_the_same_values(orders):
    modalities = comunicacion.modality_table(orders)
    extremes = comunicacion.extreme_summary(orders)
    concentration = comunicacion.concentration_table(orders)
    dependence = comunicacion.dependence_table(orders, min_orders=1)
    assert (dependence["top2_pct"] >= dependence["top1_pct"]).all()
    assert dependence["top2_pct"].le(100).all()
    findings = comunicacion.findings_table(modalities, extremes, concentration, dependence, min_orders=1)
    row = findings[(findings["indicador"] == "extremos_porcentaje_monto")].iloc[0]
    assert row["valor"] == pytest.approx(extremes["porcentaje_monto"])
    assert "NombreProveedor" not in findings.columns
    assert set(findings.loc[findings["indicador"] == "unidades_analizadas", "grupo"]) == {"mínimo 1 orden"}
    assert (dependence["ordenes_top1"] <= dependence["ordenes"]).all()


def test_figures_have_labels_legend_and_source(orders, tmp_path):
    modalities = comunicacion.modality_table(orders)
    extremes = comunicacion.extreme_summary(orders)
    concentration = comunicacion.concentration_table(orders)
    figures = (
        comunicacion.plot_modalities(modalities),
        comunicacion.plot_extremes(comunicacion.extreme_histogram_table(orders), extremes),
        comunicacion.plot_concentration(concentration),
    )
    try:
        for number, fig in enumerate(figures):
            assert fig._suptitle is not None or fig.axes[0].get_title()
            assert all(ax.get_xlabel() for ax in fig.axes)
            assert any(ax.get_ylabel() for ax in fig.axes)
            assert fig.legends or any(ax.get_legend() for ax in fig.axes)
            assert any("Fuente:" in text.get_text() for text in fig.texts)
            target = tmp_path / f"figure_{number}.png"
            comunicacion.save_figure(fig, target)
            assert target.stat().st_size > 0
    finally:
        for fig in figures:
            plt.close(fig)


def test_rejects_unprocessed_and_empty_inputs(orders, tmp_path):
    with pytest.raises(FileNotFoundError, match="F2/04_transformacion"):
        comunicacion.read_processed_orders(tmp_path / "missing.csv")
    with pytest.raises(KeyError, match="Faltan columnas"):
        comunicacion.modality_table(orders.drop(columns=["modalidad"]))
    with pytest.raises(ValueError, match="Código único"):
        comunicacion.modality_table(pd.concat([orders, orders.iloc[[0]]], ignore_index=True))
    with pytest.raises(ValueError, match="intervalos"):
        comunicacion.extreme_histogram_table(orders, bins=1)
    empty = comunicacion.dependence_table(orders, min_orders=len(orders) + 1)
    assert empty.empty
    findings = comunicacion.findings_table(
        comunicacion.modality_table(orders), comunicacion.extreme_summary(orders),
        comunicacion.concentration_table(orders), empty, min_orders=len(orders) + 1,
    )
    assert (findings.loc[findings["indicador"] == "unidades_analizadas", "valor"] == 0).all()


@pytest.fixture
def extreme_detail_case(orders):
    sample = orders.copy().reset_index(drop=True)
    sample["monto_extremo"] = False
    sample.loc[:1, "monto_extremo"] = True
    sample.loc[:1, ordenes.AMOUNT_COLUMN] = [100.0, 300.0]
    rows = []
    for position, rubro, net in [(0, "A", 10.0), (0, "B", 30.0), (1, "A", 5.0), (1, "A", 15.0)]:
        row = sample.iloc[position]
        rows.append({"periodo": row["periodo"], "Codigo": row["Codigo"],
                     "RubroN1": "General", "RubroN2": rubro,
                     "monedaItem": "CLF" if position == 0 else "CLP", "totalLineaNeto": net})
    return sample, pd.DataFrame(rows)


def test_oe5_allocates_each_order_once_and_uses_total_denominator(extreme_detail_case):
    sample, lines = extreme_detail_case
    table = comunicacion.extreme_product_table(sample, lines, top=None).set_index("RubroN2")
    assert table.loc["A", "monto_asignado_clp"] == pytest.approx(325)
    assert table.loc["B", "monto_asignado_clp"] == pytest.approx(75)
    assert table["monto_asignado_clp"].sum() == pytest.approx(400)
    assert table.loc["A", "ordenes_con_rubro"] == 2
    top = comunicacion.extreme_product_table(sample, lines, top=1)
    assert top.iloc[0]["porcentaje_monto_extremo"] == pytest.approx(81.25)
    tables = comunicacion.extreme_breakdown_tables(sample)
    assert tables["modalidad"]["ordenes"].sum() == 2
    assert tables["modalidad"]["monto_extremo_clp"].sum() == pytest.approx(400)
    assert tables["modalidad"]["porcentaje_monto_extremo"].sum() == pytest.approx(100)
    assert tables["unidad"]["monto_extremo_clp"].sum() == pytest.approx(400)


def test_oe5_rejects_incomplete_or_incomparable_detail(extreme_detail_case):
    sample, lines = extreme_detail_case
    with pytest.raises(ValueError, match="Falta detalle"):
        comunicacion.extreme_product_table(sample, lines.iloc[:2])
    mixed = lines.copy()
    mixed.loc[0, "monedaItem"] = "CLP"
    with pytest.raises(ValueError, match="monedas distintas"):
        comunicacion.extreme_product_table(sample, mixed)
    zero = lines.copy()
    zero.loc[:1, "totalLineaNeto"] = 0
    with pytest.raises(ValueError, match="neto de líneas positivo"):
        comunicacion.extreme_product_table(sample, zero)
    sample["monto_extremo"] = False
    with pytest.raises(ValueError, match="órdenes extremas"):
        comunicacion.extreme_breakdown_tables(sample)


def test_oe5_reads_only_selected_orders_with_source_encoding(extreme_detail_case, tmp_path):
    sample, lines = extreme_detail_case
    for period in comunicacion.PERIODS:
        part = lines.loc[lines["periodo"].eq(period)].drop(columns="periodo").copy()
        part["RubroN2"] = "Prótesis"
        part["totalLineaNeto"] = part["totalLineaNeto"].astype(str).str.replace(".", ",", regex=False)
        part.to_csv(tmp_path / f"oc_{period}_salud_valparaiso.csv", sep=";", encoding="latin-1", index=False)
    loaded = comunicacion.read_extreme_product_lines(tmp_path, sample)
    assert len(loaded) == 4
    assert loaded["RubroN2"].eq("Prótesis").all()
    assert loaded["totalLineaNeto"].sum() == pytest.approx(60)
