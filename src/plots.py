"""Figuras estáticas de respaldo (requisito 14).

Nota: matplotlib no pertenece al stack fijo del proyecto y su uso está
pendiente de la decisión del equipo (supuesto A1). Este módulo no lo añade a
`requirements.txt`; las funciones de cálculo de este archivo no lo necesitan.

Las cifras se calculan solo desde `outputs/plays_enriched.csv`. No se abre
ningún archivo de tracking. Se reutilizan `wilson_ci`, `diff_props_ci`,
`quartile_edges`, `assign_bins` y `merge_small_bins` de `src.analyze`, las
mismas fórmulas de `outputs/COACH_INSIGHTS.md`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Permite `python src/plots.py` desde la raíz (sys.path[0] sería src/).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.analyze import (  # noqa: E402
    FLAG_INCONCLUSIVE,
    MIN_N,
    _bite_labels,
    assign_bins,
    diff_props_ci,
    merge_small_bins,
    quartile_edges,
    wilson_ci,
)

ROOT = Path(__file__).resolve().parent.parent
PLAYS_PATH = ROOT / "outputs" / "plays_enriched.csv"

REQUIRED_COLUMNS = (
    "pff_passCoverage", "lb_bite_yards", "defendersInBox", "protection_advantage",
    "any_pressure", "is_success", "pff_playAction", "is_blitz",
)

LABEL_INCONCLUSIVE = FLAG_INCONCLUSIVE  # "no concluyente"

DIFF_COLUMNS = ["label", "n_pa", "n_trad", "diff_pp", "lo_pp", "hi_pp", "no_concluyente"]
PROT_COLUMNS = [
    "categoria", "grupo", "n", "pressure_pct", "pressure_lo", "pressure_hi",
    "success_pct", "success_lo", "success_hi", "no_concluyente",
]


def _fail(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    sys.exit(code)


def load_plays(path: Path | str = PLAYS_PATH) -> pd.DataFrame:
    """Lee el CSV enriquecido. Sale con código 1 y mensaje en español si falla."""
    path = Path(path)
    if not path.is_file():
        _fail(f"Error: no existe el archivo outputs/plays_enriched.csv (ruta buscada: {path}).")
    try:
        df = pd.read_csv(path)
    except Exception as exc:  # archivo ilegible
        _fail(f"Error: no se pudo leer outputs/plays_enriched.csv: {exc}")
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            _fail(f"Error: falta la columna requerida '{col}' en outputs/plays_enriched.csv.")
    return df


def _num(df: pd.DataFrame, col: str) -> pd.Series:
    s = pd.to_numeric(df[col], errors="coerce")
    return s.where(np.isfinite(s))


def _pa_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Jugadas con play action válido (0 o 1) y `is_success` numérico."""
    d = df.copy()
    d["_pa"] = _num(d, "pff_playAction")
    d["_succ"] = _num(d, "is_success")
    return d[d["_pa"].isin([0, 1])]


def _diff_row(label: str, sub: pd.DataFrame) -> dict:
    """Diferencia de Success_Rate (PA menos Tradicional) en pp para un subconjunto."""
    s1 = sub.loc[sub["_pa"] == 1, "_succ"].dropna()
    s0 = sub.loc[sub["_pa"] == 0, "_succ"].dropna()
    n1, n0 = int((sub["_pa"] == 1).sum()), int((sub["_pa"] == 0).sum())
    d = diff_props_ci(int(round(s1.sum())), int(s1.size), int(round(s0.sum())), int(s0.size))
    pp = lambda v: float("nan") if v is None else v * 100.0  # noqa: E731
    return {
        "label": label, "n_pa": n1, "n_trad": n0,
        "diff_pp": pp(d.diff), "lo_pp": pp(d.lo), "hi_pp": pp(d.hi),
        "no_concluyente": bool(n1 < MIN_N or n0 < MIN_N),
    }


def cells_fig1(df: pd.DataFrame) -> pd.DataFrame:
    """Figura 1: diferencia de Success_Rate PA menos Tradicional por `pff_passCoverage`."""
    d = _pa_frame(df)
    cov = d["pff_passCoverage"]
    rows = [_diff_row(str(v), d[cov == v]) for v in sorted(cov.dropna().unique(), key=str)]
    return pd.DataFrame(rows, columns=DIFF_COLUMNS)


def cells_fig2(df: pd.DataFrame) -> pd.DataFrame:
    """Figura 2: diferencia por rango de `lb_bite_yards` y por `defendersInBox`.

    Columna extra `variable`: "lb_bite_yards" o "defendersInBox".
    """
    d = _pa_frame(df)
    rows: list[dict] = []

    bite = _num(d, "lb_bite_yards")
    edges = quartile_edges(bite)
    if edges:
        idx = pd.Series(assign_bins(bite, edges), index=d.index).where(bite.notna())
        for i, lab in enumerate(_bite_labels(edges)):
            sub = d[idx == i]
            if len(sub):
                rows.append({"variable": "lb_bite_yards", **_diff_row(lab, sub)})

    box = _num(d, "defendersInBox").round()
    for v in sorted(box.dropna().unique()):
        rows.append({"variable": "defendersInBox", **_diff_row(str(int(v)), d[box == v])})
    return pd.DataFrame(rows, columns=["variable", *DIFF_COLUMNS])


def _prop_pct(k: float, n: int) -> tuple[float, float, float]:
    """(porcentaje, lo, hi) de Wilson en 0 a 100; NaN si n == 0."""
    ci = wilson_ci(int(round(k)), n)
    if ci is None:
        return float("nan"), float("nan"), float("nan")
    return k / n * 100.0, ci[0] * 100.0, ci[1] * 100.0


def cells_fig3(df: pd.DataFrame) -> pd.DataFrame:
    """Figura 3: `any_pressure` y Success_Rate por `protection_advantage`, Blitz y No Blitz.

    Las categorías se fusionan una sola vez sobre el total (igual que COACH_INSIGHTS.md).
    """
    d = df.copy()
    d["_blitz"] = _num(d, "is_blitz")
    d["_prot"] = _num(d, "protection_advantage")
    d["_press"] = _num(d, "any_pressure")
    d["_succ"] = _num(d, "is_success")

    prot_all = d["_prot"].dropna().round().astype("int64")
    bins = merge_small_bins(prot_all.value_counts().sort_index())
    d["_prot"] = d["_prot"].round()
    d = d[d["_blitz"].isin([0, 1])]

    rows: list[dict] = []
    for lo, hi in bins:
        cat = str(lo) if lo == hi else f"{lo} a {hi}"
        in_cat = d[(d["_prot"] >= lo) & (d["_prot"] <= hi)]
        for blitz, group in ((1, "Blitz"), (0, "No Blitz")):
            sub = in_cat[in_cat["_blitz"] == blitz]
            p = sub["_press"].dropna()
            s = sub["_succ"].dropna()
            pp, plo, phi = _prop_pct(p.sum(), int(p.size))
            sp, slo, shi = _prop_pct(s.sum(), int(s.size))
            rows.append({
                "categoria": cat, "grupo": group, "n": int(len(sub)),
                "pressure_pct": pp, "pressure_lo": plo, "pressure_hi": phi,
                "success_pct": sp, "success_lo": slo, "success_hi": shi,
                "no_concluyente": bool(len(sub) < MIN_N),
            })
    return pd.DataFrame(rows, columns=PROT_COLUMNS)


# --------------------------------------------------------------------------
# Dibujo (matplotlib se importa de forma perezosa, supuesto A1)
# --------------------------------------------------------------------------
OUT_FILES = (
    ROOT / "outputs" / "fig1_play_action_coverage.png",
    ROOT / "outputs" / "fig2_lb_bite_box.png",
    ROOT / "outputs" / "fig3_blitz_protection.png",
)
DPI = 300
COLOR_POS, COLOR_NEG, COLOR_INCONC = "#2a7f62", "#b5483a", "#aaaaaa"


def _import_pyplot():
    """Importa matplotlib con backend Agg. Sale con código 2 si no está instalado."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        _fail(
            "Error: no está instalada la dependencia 'matplotlib', necesaria para "
            "generar las figuras. Instálela (pip install matplotlib) y vuelva a ejecutar.",
            code=2,
        )
    return plt


def _diff_bars(ax, cells: pd.DataFrame, title: str, xlabel: str) -> None:
    """Barras horizontales de diferencia (pp) con IC y n visibles."""
    ax.axvline(0, color="black", linewidth=0.8)
    ys = list(range(len(cells)))
    for y, row in zip(ys, cells.itertuples(index=False)):
        if pd.isna(row.diff_pp):
            ax.text(0, y, "sin datos suficientes", va="center", ha="left", fontsize=8, color="#666666")
            continue
        color = COLOR_INCONC if row.no_concluyente else (COLOR_POS if row.diff_pp >= 0 else COLOR_NEG)
        ax.barh(y, row.diff_pp, color=color, alpha=0.85)
        if not (pd.isna(row.lo_pp) or pd.isna(row.hi_pp)):
            ax.errorbar(row.diff_pp, y, xerr=[[row.diff_pp - row.lo_pp], [row.hi_pp - row.diff_pp]],
                        fmt="none", ecolor="black", capsize=3, linewidth=1)
    labels = []
    for row in cells.itertuples(index=False):
        extra = f"\n{LABEL_INCONCLUSIVE}" if row.no_concluyente else ""
        labels.append(f"{row.label}\n(n PA={row.n_pa}, n trad.={row.n_trad}){extra}")
    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.set_title(title, fontsize=11)
    ax.grid(axis="x", alpha=0.3)


_XLABEL_DIFF = "Diferencia de Success_Rate, play action menos tradicional (pp), con IC 95 %"


def draw_fig1(cells: pd.DataFrame, out_path: Path | str | None = None):
    """Figura 1: diferencia PA menos tradicional por cobertura."""
    plt = _import_pyplot()
    fig, ax = plt.subplots(figsize=(9, max(4.0, 0.9 * len(cells) + 1.5)))
    _diff_bars(ax, cells, "Play action vs. tradicional por cobertura (pff_passCoverage)", _XLABEL_DIFF)
    fig.tight_layout()
    if out_path is not None:
        fig.savefig(out_path, dpi=DPI)
    return fig


def draw_fig2(cells: pd.DataFrame, out_path: Path | str | None = None):
    """Figura 2: diferencia por rango de lb_bite_yards y por defendersInBox."""
    plt = _import_pyplot()
    parts = [
        ("lb_bite_yards", "Por avance del linebacker (lb_bite_yards, yardas)"),
        ("defendersInBox", "Por defensores en la caja (defendersInBox)"),
    ]
    sizes = [max(1, int((cells["variable"] == v).sum())) for v, _ in parts]
    fig, axes = plt.subplots(2, 1, figsize=(9, 1.0 * sum(sizes) + 4.5),
                             gridspec_kw={"height_ratios": sizes})
    for ax, (var, title) in zip(axes, parts):
        sub = cells[cells["variable"] == var].reset_index(drop=True)
        _diff_bars(ax, sub, title, _XLABEL_DIFF)
    fig.tight_layout()
    if out_path is not None:
        fig.savefig(out_path, dpi=DPI)
    return fig


def draw_fig3(cells: pd.DataFrame, out_path: Path | str | None = None):
    """Figura 3: presión y Success_Rate por ventaja de protección, Blitz vs No Blitz.
    Se omiten las barras de celdas con n = 0 (valores NaN).
    """
    plt = _import_pyplot()
    cats = list(dict.fromkeys(cells["categoria"]))
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5), sharex=True)
    panels = [
        ("pressure", "Presión sobre el mariscal (any_pressure)", "Jugadas con presión (%)"),
        ("success", "Jugadas exitosas (is_success)", "Success_Rate (%)"),
    ]
    width = 0.38
    colors = {"Blitz": "#c0562f", "No Blitz": "#3b6ea5"}
    for ax, (pref, title, ylabel) in zip(axes, panels):
        for k, group in enumerate(("Blitz", "No Blitz")):
            offset = (k - 0.5) * width
            for i, cat in enumerate(cats):
                r = cells[(cells["categoria"] == cat) & (cells["grupo"] == group)]
                if r.empty:
                    continue
                r = r.iloc[0]
                val = r[f"{pref}_pct"]
                if pd.isna(val):
                    continue  # n = 0: sin barra
                x = i + offset
                ax.bar(x, val, width, color=colors[group], alpha=0.5 if r["no_concluyente"] else 0.9,
                       hatch="//" if r["no_concluyente"] else None, edgecolor="white")
                ax.errorbar(x, val, yerr=[[val - r[f"{pref}_lo"]], [r[f"{pref}_hi"] - val]],
                            fmt="none", ecolor="black", capsize=3, linewidth=1)
                note = f"n={int(r['n'])}" + ("\nno concluyente" if r["no_concluyente"] else "")
                ax.text(x, r[f"{pref}_hi"] + 1, note, ha="center", va="bottom", fontsize=7)
        ax.set_xticks(range(len(cats)))
        ax.set_xticklabels(cats)
        ax.set_xlabel("Ventaja de protección (protection_advantage)")
        ax.set_ylabel(ylabel + ", IC 95 %")
        ax.set_title(title, fontsize=11)
        ax.set_ylim(0, 115)
        ax.grid(axis="y", alpha=0.3)
        from matplotlib.patches import Patch

        ax.legend([Patch(color=colors[g]) for g in colors], list(colors), loc="upper right")
    fig.suptitle("Protección y blitz: presión y éxito de la jugada (barras rayadas: no concluyente)")
    fig.tight_layout()
    if out_path is not None:
        fig.savefig(out_path, dpi=DPI)
    return fig


def main() -> None:
    df = load_plays()
    _import_pyplot()  # sale con código 2 antes de escribir cualquier PNG
    figs = [
        draw_fig1(cells_fig1(df)),
        draw_fig2(cells_fig2(df)),
        draw_fig3(cells_fig3(df)),
    ]
    for fig, path in zip(figs, OUT_FILES):  # solo se escribe tras renderizar todo
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=DPI)
    for path in OUT_FILES:
        print(path)
    sys.exit(0)


if __name__ == "__main__":
    main()
