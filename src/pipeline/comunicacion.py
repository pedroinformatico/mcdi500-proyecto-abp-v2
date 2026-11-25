"""Tablas verificables y figuras explicativas de la Fase 4.

Todas las funciones reciben órdenes ya procesadas: una fila por orden, montos
en pesos nominales y la marca de extremo calculada por el pipeline de F2.
No limpian, reclasifican ni vuelven a ajustar el pipeline.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from . import ordenes

AMOUNT = ordenes.AMOUNT_COLUMN
PERIODS = ("2024-09", "2025-09")
MODALITIES = ordenes.MODALITIES
COLORS = {
    "Compra ágil": "#0072B2",
    "Trato directo": "#D55E00",
    "Convenio marco": "#009E73",
    "Licitación": "#CC79A7",
    "Otra": "#767676",
}
SOURCE = "Fuente: elaboración propia con órdenes de ChileCompra, septiembre de 2024 y 2025."


def read_processed_orders(path: Path) -> pd.DataFrame:
    """Lee la salida de F2; conserva etiquetas y pesos, sin repetir la limpieza."""
    if not path.is_file():
        raise FileNotFoundError(f"Falta {path}; ejecute primero F2/04_transformacion.ipynb.")
    orders = pd.read_csv(
        path,
        dtype={"Codigo": "string", "CodigoProveedor": "string", "CodigoUnidadCompra": "string"},
    )
    validate_visual_input(orders)
    return orders


def validate_visual_input(orders: pd.DataFrame) -> None:
    """Rechaza una tabla que no represente las órdenes procesadas del estudio."""
    required = {"periodo", "Codigo", "modalidad", AMOUNT, "monto_extremo", "CodigoProveedor", "CodigoUnidadCompra", "UnidadCompra"}
    missing = required.difference(orders.columns)
    if missing:
        raise KeyError(f"Faltan columnas procesadas: {', '.join(sorted(missing))}")
    if orders.empty or orders["Codigo"].isna().any() or not orders["Codigo"].is_unique:
        raise ValueError("Se requiere una fila por orden, con Código único y no ausente.")
    if set(orders["periodo"]) != set(PERIODS):
        raise ValueError("Se requieren los períodos 2024-09 y 2025-09.")
    if not orders["modalidad"].isin(MODALITIES).all():
        raise ValueError("Hay modalidades fuera de las categorías del pipeline.")
    if orders[[AMOUNT, "CodigoProveedor", "CodigoUnidadCompra", "monto_extremo"]].isna().any().any():
        raise ValueError("Hay valores ausentes en las variables necesarias para las figuras.")
    if not pd.api.types.is_numeric_dtype(orders[AMOUNT]) or (orders[AMOUNT] < 0).any():
        raise ValueError("El monto procesado debe ser numérico y no negativo.")
    if not pd.api.types.is_bool_dtype(orders["monto_extremo"]):
        raise ValueError("La marca monto_extremo debe ser booleana.")


def modality_table(orders: pd.DataFrame) -> pd.DataFrame:
    """Número, monto y porcentaje dentro de cada período y modalidad."""
    validate_visual_input(orders)
    grouped = orders.groupby(["periodo", "modalidad"]).agg(
        ordenes=("Codigo", "size"), monto_pesos=(AMOUNT, "sum")
    )
    index = pd.MultiIndex.from_product([PERIODS, MODALITIES], names=["periodo", "modalidad"])
    result = grouped.reindex(index, fill_value=0).reset_index()
    result["porcentaje_ordenes"] = result["ordenes"] / result.groupby("periodo")["ordenes"].transform("sum") * 100
    result["porcentaje_monto"] = result["monto_pesos"] / result.groupby("periodo")["monto_pesos"].transform("sum") * 100
    return result


def plot_modalities(table: pd.DataFrame) -> Figure:
    """Dos barras apiladas al 100 %: frecuencia y monto, con igual color por modalidad."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    for ax, column, label in zip(
        axes, ("porcentaje_ordenes", "porcentaje_monto"), ("Número de órdenes", "Monto en pesos nominales")
    ):
        left = np.zeros(len(PERIODS))
        for modality in MODALITIES:
            values = table.loc[table["modalidad"] == modality].set_index("periodo").loc[list(PERIODS), column].to_numpy()
            ax.barh(PERIODS, values, left=left, color=COLORS[modality], label=modality, height=0.55)
            left += values
        ax.set_xlim(0, 100)
        ax.set_xlabel("Porcentaje del período (%)")
        ax.set_title(label)
        ax.grid(axis="x", alpha=0.2)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Septiembre")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(0.5, 0.045))
    fig.suptitle("La compra ágil gana participación; la licitación sigue liderando el monto", weight="bold")
    fig.text(0.02, 0.01, SOURCE + " Compra ágil se clasifica antes que trato directo en ambos años.", fontsize=8)
    fig.subplots_adjust(bottom=0.28, top=0.8, wspace=0.14)
    return fig


def extreme_summary(orders: pd.DataFrame) -> dict[str, float]:
    """Magnitud de las órdenes ya marcadas como extremas en F2."""
    validate_visual_input(orders)
    amount = orders[AMOUNT]
    extreme = orders["monto_extremo"]
    return {
        "ordenes": int(len(orders)),
        "extremas": int(extreme.sum()),
        "porcentaje_ordenes": float(extreme.mean() * 100),
        "porcentaje_monto": float(amount[extreme].sum() / amount.sum() * 100),
        "limite_pesos": float(ordenes.extreme_amount_limit(amount)),
    }


def extreme_histogram_table(orders: pd.DataFrame, bins: int = 28) -> pd.DataFrame:
    """Conteos en intervalos logarítmicos; mantiene separado el cálculo del dibujo."""
    validate_visual_input(orders)
    if bins < 2:
        raise ValueError("Se requieren al menos dos intervalos.")
    positive = orders.loc[orders[AMOUNT] > 0, AMOUNT]
    if positive.empty:
        raise ValueError("Se requieren montos positivos para la escala logarítmica.")
    edges = np.geomspace(float(positive.min()), float(positive.max()) * (1 + 1e-9), bins + 1)
    counts, _ = np.histogram(positive, bins=edges)
    return pd.DataFrame({"desde_pesos": edges[:-1], "hasta_pesos": edges[1:], "ordenes": counts})


def plot_extremes(table: pd.DataFrame, summary: dict[str, float]) -> Figure:
    """Histograma con umbral y conteo; el área no representa el monto acumulado."""
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.bar(table["desde_pesos"], table["ordenes"], width=table["hasta_pesos"] - table["desde_pesos"],
           align="edge", color="#9FB6C8", edgecolor="white", label="Órdenes")
    ax.axvline(summary["limite_pesos"], color="#B2182B", linewidth=2, linestyle="--",
               label=f"Umbral extremo: ${summary['limite_pesos']/1e6:.1f} millones")
    ax.set_xscale("log")
    ax.set_xlim(table["desde_pesos"].min(), table["hasta_pesos"].max())
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Monto por orden (pesos nominales, escala logarítmica)")
    ax.set_ylabel("Número de órdenes")
    ax.set_title(f"{summary['extremas']:,} órdenes extremas reúnen {summary['porcentaje_monto']:.1f} % del monto", weight="bold")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.2)
    fig.text(0.02, 0.01, SOURCE + " Extremos: marca del pipeline F2 (IQR sobre log10 del monto).", fontsize=8)
    fig.subplots_adjust(bottom=0.22, top=0.86)
    return fig


def concentration_table(orders: pd.DataFrame, top: int = 10) -> pd.DataFrame:
    """Curva acumulada de los mayores proveedores, calculada en cada escenario."""
    validate_visual_input(orders)
    if top < 1:
        raise ValueError("top debe ser positivo.")
    records = []
    for period in PERIODS:
        for scenario, subset in (
            ("Todas", orders[orders["periodo"] == period]),
            ("Sin extremas", orders[(orders["periodo"] == period) & ~orders["monto_extremo"]]),
        ):
            amounts = subset.groupby("CodigoProveedor")[AMOUNT].sum().sort_values(ascending=False)
            total = float(amounts.sum())
            if total <= 0:
                raise ValueError(f"Monto total no positivo en {period}, {scenario}.")
            for rank, value in enumerate(amounts.head(top).cumsum() / total * 100, start=1):
                records.append({"periodo": period, "escenario": scenario, "mayores": rank,
                                "participacion_acumulada_pct": float(value), "ordenes": len(subset),
                                "proveedores": len(amounts)})
    return pd.DataFrame(records)


def plot_concentration(table: pd.DataFrame) -> Figure:
    """Cuatro curvas con el mismo eje, un color por año y trazo por escenario."""
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    colors = {PERIODS[0]: "#0072B2", PERIODS[1]: "#D55E00"}
    for period in PERIODS:
        for scenario, style in (("Todas", "-"), ("Sin extremas", "--")):
            part = table[(table["periodo"] == period) & (table["escenario"] == scenario)]
            ax.plot(part["mayores"], part["participacion_acumulada_pct"], marker="o", markersize=3,
                    color=colors[period], linestyle=style, linewidth=2, label=f"{period} · {scenario}")
    last = int(table["mayores"].max())
    ax.set_xlim(1, last)
    ax.set_ylim(bottom=0)
    ax.set_xticks(range(1, last + 1))
    ax.set_xlabel("Número de mayores proveedores (ordenados por monto en cada escenario)")
    ax.set_ylabel("Participación acumulada del monto del período (%)")
    ax.set_title("El aumento del top 10 desaparece al excluir órdenes extremas", weight="bold")
    ax.grid(alpha=0.2)
    ax.legend(title="Período · escenario", frameon=False)
    fig.text(0.02, 0.01, SOURCE + " Cada curva reordena proveedores en su período y escenario.", fontsize=8)
    fig.subplots_adjust(bottom=0.22, top=0.88)
    return fig


def dependence_table(orders: pd.DataFrame, min_orders: int = 20) -> pd.DataFrame:
    """Dependencia por unidad: cuota de sus uno y dos principales proveedores."""
    validate_visual_input(orders)
    if min_orders < 1:
        raise ValueError("min_orders debe ser positivo.")
    grouped = orders.groupby(["periodo", "CodigoUnidadCompra", "CodigoProveedor"])[AMOUNT].sum()
    records = []
    for (period, unit), part in orders.groupby(["periodo", "CodigoUnidadCompra"]):
        if len(part) < min_orders:
            continue
        amounts = grouped.loc[(period, unit)].sort_values(ascending=False)
        total = float(amounts.sum())
        if total <= 0:
            continue
        supplier = str(amounts.index[0])
        records.append({"periodo": period, "unidad": str(part["UnidadCompra"].iloc[0]),
                        "codigo_unidad": str(unit), "ordenes": len(part), "proveedores": len(amounts),
                        "codigo_proveedor_top1": supplier,
                        "ordenes_top1": int((part["CodigoProveedor"] == supplier).sum()),
                        "top1_pct": float(amounts.iloc[0] / total * 100),
                        "top2_pct": float(amounts.head(2).sum() / total * 100)})
    columns = ["periodo", "unidad", "codigo_unidad", "ordenes", "proveedores",
               "codigo_proveedor_top1", "ordenes_top1", "top1_pct", "top2_pct"]
    return pd.DataFrame(records, columns=columns).sort_values(
        ["periodo", "top1_pct"], ascending=[True, False]
    ).reset_index(drop=True)


def findings_table(modalities: pd.DataFrame, extremes: dict[str, float],
                   concentration: pd.DataFrame, dependence: pd.DataFrame,
                   min_orders: int = 20) -> pd.DataFrame:
    """Cifras únicas para citar en notebook, informe y guion; sin nombres personales."""
    records = []
    for row in modalities.itertuples(index=False):
        for metric, value, unit in (
            ("ordenes_modalidad", row.ordenes, "órdenes"),
            ("participacion_ordenes_modalidad", row.porcentaje_ordenes, "%"),
            ("monto_modalidad", row.monto_pesos, "CLP nominales"),
            ("participacion_monto_modalidad", row.porcentaje_monto, "%"),
        ):
            records.append((metric, row.periodo, row.modalidad, float(value), unit))
    for metric, unit in (("ordenes", "órdenes"), ("extremas", "órdenes"),
                         ("porcentaje_ordenes", "%"), ("porcentaje_monto", "%"),
                         ("limite_pesos", "CLP nominales")):
        records.append((f"extremos_{metric}", "Ambos", "Todas", float(extremes[metric]), unit))
    for row in concentration[concentration["mayores"] == 10].itertuples(index=False):
        records.append(("participacion_top10", row.periodo, row.escenario,
                        float(row.participacion_acumulada_pct), "%"))
    for period in PERIODS:
        part = dependence[dependence["periodo"] == period]
        group = f"mínimo {min_orders} {'orden' if min_orders == 1 else 'órdenes'}"
        records.extend([
            ("unidades_analizadas", period, group, float(len(part)), "unidades"),
            ("unidades_top1_mayor_50pct", period, group, float((part["top1_pct"] > 50).sum()), "unidades"),
            ("unidades_top2_mayor_75pct", period, group, float((part["top2_pct"] > 75).sum()), "unidades"),
        ])
    return pd.DataFrame(records, columns=["indicador", "periodo", "grupo", "valor", "unidad"])


def save_figure(fig: Figure, path: Path) -> None:
    """Exporta la misma figura que se muestra en el notebook para informe y video."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
