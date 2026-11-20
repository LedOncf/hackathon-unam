"""Orquestación del pipeline Coach, estadística y reporte.

Este módulo no ejecuta código al importarse. Esta primera parte contiene la
estadística base (tarea 5.1): intervalos de Wilson, de la media, de Welch y de
Newcombe, y el resumen de celdas con sus etiquetas.
"""

from __future__ import annotations

import importlib.util
import logging
import math
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

from src.features import OUTPUT_DIR, PipelineError, RunReport

logger = logging.getLogger(__name__)

Z95 = 1.96
MIN_N = 30

FLAG_INCONCLUSIVE = "no concluyente"
FLAG_INSUFFICIENT = "n insuficiente"
FLAG_NOT_COMPUTABLE = "no calculable"
FLAG_UNAVAILABLE = "no disponible"


@dataclass
class CellStats:
    """Estadísticos de una Celda."""

    label: str
    n: int
    mean: float | None = None
    mean_lo: float | None = None
    mean_hi: float | None = None
    success_rate: float | None = None
    sr_lo: float | None = None
    sr_hi: float | None = None
    flags: list[str] = field(default_factory=list)


@dataclass
class DiffStats:
    """Comparación grupo 1 menos grupo 0."""

    n1: int
    n0: int
    diff: float | None = None
    lo: float | None = None
    hi: float | None = None
    flags: list[str] = field(default_factory=list)


def _clean(values) -> np.ndarray:
    """Convierte a float64 y descarta nulos y no finitos."""
    arr = np.asarray(values, dtype="float64").ravel()
    return arr[np.isfinite(arr)]


def wilson_ci(k: int, n: int, z: float = Z95) -> tuple[float, float] | None:
    """IC de Wilson para una proporción. Devuelve None si n == 0."""
    if n <= 0:
        return None
    p = k / n
    z2 = z * z
    den = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / den
    half = z * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n)) / den
    return max(0.0, center - half), min(1.0, center + half)


def mean_ci(x, z: float = Z95) -> tuple[float, float, float] | None:
    """(media, lo, hi) con media ± z·s/√n, s con ddof=1. None si n < 2."""
    arr = _clean(x)
    n = arr.size
    if n < 2:
        return None
    m = float(arr.mean())
    half = z * float(arr.std(ddof=1)) / math.sqrt(n)
    return m, m - half, m + half


def summarize_cell(
    values,
    kind: Literal["binary", "continuous"],
    label: str,
    block: Literal["A", "B"] = "A",
    success=None,
) -> CellStats:
    """Resume una Celda.

    `values` es la métrica de interés (nulos se descartan). Si `kind` es
    "binary" la media es una proporción con IC de Wilson; si es "continuous",
    el IC es media ± 1.96·s/√n. `success` (opcional) son los valores de
    `is_success` de la Celda y llena `success_rate` con su IC de Wilson.

    Etiquetas: bloque A, n < 30 "no concluyente" y n ≤ 1 IC "no disponible".
    Bloque B, n < 30 "n insuficiente" (se omite el IC y se conserva n) y
    métrica continua con varianza cero "no calculable" (se omite el IC).
    """
    if kind not in ("binary", "continuous"):
        raise ValueError(f"kind inválido: {kind!r}")
    if block not in ("A", "B"):
        raise ValueError(f"block inválido: {block!r}")

    arr = _clean(values)
    n = int(arr.size)
    cell = CellStats(label=label, n=n)
    if n > 0:
        cell.mean = float(arr.mean())

    small = n < MIN_N
    ci_allowed = True
    if block == "A":
        if small:
            cell.flags.append(FLAG_INCONCLUSIVE)
        if n <= 1:
            cell.flags.append(FLAG_UNAVAILABLE)
            ci_allowed = False
    else:
        if small:
            cell.flags.append(FLAG_INSUFFICIENT)
            ci_allowed = False
        elif kind == "continuous" and float(arr.std(ddof=1)) == 0.0:
            cell.flags.append(FLAG_NOT_COMPUTABLE)
            ci_allowed = False

    if ci_allowed:
        if kind == "binary":
            ci = wilson_ci(int(round(arr.sum())), n)
            if ci is not None:
                cell.mean_lo, cell.mean_hi = ci
        else:
            res = mean_ci(arr)
            if res is not None:
                _, cell.mean_lo, cell.mean_hi = res

    if success is not None:
        s = _clean(success)
        ns = int(s.size)
        if ns > 0:
            k = int(round(s.sum()))
            cell.success_rate = k / ns
            if ci_allowed and ns >= 2:
                cell.sr_lo, cell.sr_hi = wilson_ci(k, ns)  # type: ignore[misc]
    return cell


def diff_means_ci(x1, x0, z: float = Z95) -> DiffStats:
    """Diferencia de medias (grupo 1 menos 0) con IC de Welch.

    Un grupo vacío deja diferencia e IC nulos. Con un grupo de una sola
    jugada se conserva la diferencia puntual y el IC queda "no disponible".
    """
    a, b = _clean(x1), _clean(x0)
    n1, n0 = int(a.size), int(b.size)
    out = DiffStats(n1=n1, n0=n0)
    if n1 == 0 or n0 == 0:
        out.flags.append(FLAG_UNAVAILABLE)
        return out
    out.diff = float(a.mean() - b.mean())
    if n1 < 2 or n0 < 2:
        out.flags.append(FLAG_UNAVAILABLE)
        return out
    se = math.sqrt(float(a.var(ddof=1)) / n1 + float(b.var(ddof=1)) / n0)
    out.lo, out.hi = out.diff - z * se, out.diff + z * se
    return out


def diff_props_ci(k1: int, n1: int, k0: int, n0: int, z: float = Z95) -> DiffStats:
    """Diferencia de proporciones (grupo 1 menos 0), IC híbrido de Newcombe.

    La diferencia y los límites están en unidades de proporción (no puntos
    porcentuales). Mismas reglas de disponibilidad que `diff_means_ci`.
    """
    out = DiffStats(n1=int(n1), n0=int(n0))
    if n1 <= 0 or n0 <= 0:
        out.flags.append(FLAG_UNAVAILABLE)
        return out
    p1, p0 = k1 / n1, k0 / n0
    out.diff = p1 - p0
    if n1 < 2 or n0 < 2:
        out.flags.append(FLAG_UNAVAILABLE)
        return out
    l1, u1 = wilson_ci(k1, n1, z)  # type: ignore[misc]
    l0, u0 = wilson_ci(k0, n0, z)  # type: ignore[misc]
    out.lo = out.diff - math.sqrt((p1 - l1) ** 2 + (u0 - p0) ** 2)
    out.hi = out.diff + math.sqrt((u1 - p1) ** 2 + (p0 - l0) ** 2)
    return out


def quartile_edges(values) -> list[float]:
    """Bordes de rango: cuartiles 25, 50 y 75 de la muestra.

    Se descartan nulos, se redondea a 2 decimales y se deduplica. Sin valores
    devuelve una lista vacía; con valores constantes, un solo borde.
    """
    arr = _clean(values)
    if arr.size == 0:
        return []
    q = np.quantile(arr, [0.25, 0.5, 0.75])
    return sorted({round(float(v), 2) for v in q})


def assign_bins(values, edges) -> np.ndarray:
    """Índice de rango por valor, con intervalos [e_{i-1}, e_i).

    Con k bordes hay k + 1 rangos (0..k). Los valores nulos o no finitos
    reciben -1. Cada valor cae en un solo rango.
    """
    arr = np.asarray(values, dtype="float64").ravel()
    e = np.asarray(sorted(edges), dtype="float64")
    idx = np.searchsorted(e, arr, side="right").astype("int64")
    idx[~np.isfinite(arr)] = -1
    return idx


def merge_small_bins(
    counts: pd.Series, min_n: int = MIN_N, max_bins: int = 5
) -> list[tuple[int, int]]:
    """Fusiona valores enteros contiguos en categorías con n >= min_n.

    `counts` es el n por valor entero distinto (el índice son los valores).
    Devuelve una lista ordenada de (min, max) por categoría, contiguas y
    disjuntas. Reglas deterministas:

    1. Cada valor empieza como categoría propia.
    2. Mientras haya una categoría con n < min_n y más de una categoría, se
       fusiona la de menor n (en empate, la de valor menor) con su vecina
       adyacente de menor n (en empate, la de valor menor).
    3. Si quedan más de `max_bins`, se fusiona el par adyacente de menor suma
       de n (en empate, el de valores menores) hasta llegar a `max_bins`.
    4. Si el total es < min_n, queda una sola categoría.
    Sin datos devuelve una lista vacía.
    """
    counts = counts[counts > 0].sort_index()
    if counts.empty:
        return []
    cats = [[int(v), int(v), int(n)] for v, n in counts.items()]  # lo, hi, n
    if sum(c[2] for c in cats) < min_n:
        return [(cats[0][0], cats[-1][1])]

    def _merge(i: int, j: int) -> None:
        cats[i] = [cats[i][0], cats[j][1], cats[i][2] + cats[j][2]]
        del cats[j]

    while len(cats) > 1 and any(c[2] < min_n for c in cats):
        i = min((k for k in range(len(cats)) if cats[k][2] < min_n),
                key=lambda k: (cats[k][2], k))
        nbrs = [k for k in (i - 1, i + 1) if 0 <= k < len(cats)]
        j = min(nbrs, key=lambda k: (cats[k][2], k))
        _merge(min(i, j), max(i, j))

    while len(cats) > max_bins:
        i = min(range(len(cats) - 1), key=lambda k: (cats[k][2] + cats[k + 1][2], k))
        _merge(i, i + 1)

    return [(c[0], c[1]) for c in cats]


# ---------------------------------------------------------------------------
# Bloque A: play action (tarea 5.3)
# ---------------------------------------------------------------------------

PP_METRIC = "prePenaltyPlayResult"
PLAY_RESULT = "playResult"
BLOCK_A_REQUIRED = (
    "pff_playAction", PP_METRIC, PLAY_RESULT, "is_success",
    "pff_passCoverageType", "pff_passCoverage", "defendersInBox", "lb_bite_yards",
)
BITE_UNIT = "yardas"


def _r3(v):
    """Redondea a 3 decimales y convierte a tipos nativos de Python."""
    if v is None:
        return None
    if isinstance(v, (bool, np.bool_)):
        return bool(v)
    if isinstance(v, (int, np.integer)):
        return int(v)
    f = float(v)
    return None if not math.isfinite(f) else round(f, 3)


def _to_native(obj):
    """Convierte dataclasses, listas y dicts a tipos nativos con 3 decimales."""
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _to_native(getattr(obj, k)) for k in obj.__dataclass_fields__}
    if isinstance(obj, dict):
        return {str(k): _to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_native(v) for v in obj]
    if obj is None or isinstance(obj, str):
        return obj
    return _r3(obj)


@dataclass
class ComparisonCell:
    """Comparación play action (1) menos sin play action (0) en una Celda.

    `success_pp` está en puntos porcentuales; las otras dos, en yardas.
    """

    label: str
    n1: int
    n0: int
    pre_penalty: DiffStats
    play_result: DiffStats
    success_pp: DiffStats
    groups: list[CellStats] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)


@dataclass
class Breakdown:
    """Desglose del Bloque A por una variable."""

    name: str
    column: str
    excluded_null: int
    cells: list[ComparisonCell] = field(default_factory=list)
    edges: list[float] | None = None
    unit: str | None = None


@dataclass
class BlockA:
    """Resultado del Bloque A."""

    n_plays: int
    n_valid: int
    excluded_null_play_action: int
    total: ComparisonCell
    breakdowns: list[Breakdown] = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_native(self)


def _scale_pp(d: DiffStats) -> DiffStats:
    """Convierte una diferencia de proporciones a puntos porcentuales."""
    for attr in ("diff", "lo", "hi"):
        v = getattr(d, attr)
        if v is not None:
            setattr(d, attr, v * 100.0)
    return d


def _compare_cell(df: pd.DataFrame, label: str) -> ComparisonCell:
    """Compara grupo 1 contra 0 de `_pa` dentro de `df`."""
    g1 = df[df["_pa"] == 1]
    g0 = df[df["_pa"] == 0]
    pre = diff_means_ci(g1[PP_METRIC], g0[PP_METRIC])
    res = diff_means_ci(g1[PLAY_RESULT], g0[PLAY_RESULT])
    s1, s0 = _clean(g1["is_success"]), _clean(g0["is_success"])
    sr = _scale_pp(
        diff_props_ci(int(round(s1.sum())), int(s1.size), int(round(s0.sum())), int(s0.size))
    )
    groups = [
        summarize_cell(g[PP_METRIC], "continuous", name, "A", success=g["is_success"])
        for name, g in (("play action", g1), ("sin play action", g0))
    ]
    flags = [FLAG_INCONCLUSIVE] if (len(g1) < MIN_N or len(g0) < MIN_N) else []
    return ComparisonCell(
        label=label, n1=int(len(g1)), n0=int(len(g0)),
        pre_penalty=pre, play_result=res, success_pp=sr, groups=groups, flags=flags,
    )


def _breakdown(
    d: pd.DataFrame, run: RunReport | None, name: str, column: str, key: pd.Series,
    labels: list[tuple[object, str]],
) -> Breakdown:
    """Una Celda por cada (valor, etiqueta) de `labels` sobre la clave `key`."""
    null = key.isna()
    n_null = int(null.sum())
    if run is not None:
        run.add(f"block_a_excluded_null_{name}", n_null)
    cells = [_compare_cell(d[key == v], lab) for v, lab in labels]
    return Breakdown(name=name, column=column, excluded_null=n_null, cells=cells)


def _bite_labels(edges: list[float]) -> list[str]:
    k = len(edges)
    out = [f"< {edges[0]:.2f}"]
    out += [f"[{edges[i - 1]:.2f}, {edges[i]:.2f})" for i in range(1, k)]
    out.append(f">= {edges[-1]:.2f}")
    return out


def build_block_a(master: pd.DataFrame, run: RunReport | None = None) -> BlockA:
    """Bloque A: play action (1) contra sin play action (0).

    Universo: jugadas con `pff_playAction` no nulo (las excluidas se cuentan).
    Cada desglose excluye y declara las jugadas con nulo en su variable. La
    diferencia de tasa de éxito está en puntos porcentuales.
    """
    run = run if run is not None else RunReport()
    missing = [c for c in BLOCK_A_REQUIRED if c not in master.columns]
    if missing:
        raise PipelineError(f"Faltan columnas para el Bloque A: {missing}")

    n_plays = int(len(master))
    d = master.copy()
    d["_pa"] = pd.to_numeric(d["pff_playAction"], errors="coerce")
    for c in (PP_METRIC, PLAY_RESULT, "is_success", "lb_bite_yards"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["_box"] = pd.to_numeric(d["defendersInBox"], errors="coerce")
    d = d[d["_pa"].isin([0, 1])]
    n_valid = int(len(d))
    excluded = n_plays - n_valid
    run.add("block_a_excluded_play_action", excluded)

    block = BlockA(
        n_plays=n_plays, n_valid=n_valid, excluded_null_play_action=excluded,
        total=_compare_cell(d, "Total"),
    )

    block.breakdowns.append(_breakdown(
        d, run, "coverage_type", "pff_passCoverageType", d["pff_passCoverageType"],
        [("Man", "Man"), ("Zone", "Zone")],
    ))

    cov = d["pff_passCoverage"]
    block.breakdowns.append(_breakdown(
        d, run, "coverage", "pff_passCoverage", cov,
        [(v, str(v)) for v in sorted(cov.dropna().unique(), key=str)],
    ))

    box = d["_box"].round()
    box = box.where(d["_box"].notna())
    block.breakdowns.append(_breakdown(
        d, run, "defenders_in_box", "defendersInBox", box,
        [(v, str(int(v))) for v in sorted(box.dropna().unique())],
    ))

    bite = d["lb_bite_yards"]
    n_null = int(bite.isna().sum())
    run.add("block_a_excluded_null_lb_bite", n_null)
    edges = quartile_edges(bite)
    bd = Breakdown(
        name="lb_bite_range", column="lb_bite_yards", excluded_null=n_null,
        edges=edges, unit=BITE_UNIT,
    )
    if edges:
        idx = pd.Series(assign_bins(bite, edges), index=d.index)
        idx = idx.where(bite.notna())
        names = _bite_labels(edges)
        for i, lab in enumerate(names):
            sub = d[idx == i]
            if len(sub):
                bd.cells.append(_compare_cell(sub, lab))
    block.breakdowns.append(bd)
    return block


# ---------------------------------------------------------------------------
# Bloque B: blitz y bolsillo (tarea 5.4)
# ---------------------------------------------------------------------------

BLOCK_B_METRICS: tuple[tuple[str, Literal["binary", "continuous"]], ...] = (
    ("any_pressure", "binary"),
    ("min_rusher_dist_at_throw", "continuous"),
    ("time_to_throw", "continuous"),
    ("is_success", "binary"),
)
BLOCK_B_REQUIRED = (
    "is_blitz", "protection_advantage", "pff_passCoverage", "offenseFormation",
    *(m for m, _ in BLOCK_B_METRICS),
)


@dataclass
class MetricComparison:
    """Blitz (1) contra no blitz (0) para una métrica.

    `excluded_null` cuenta las jugadas del conjunto con nulo en la métrica.
    """

    metric: str
    kind: str
    excluded_null: int
    blitz: CellStats
    no_blitz: CellStats
    diff: DiffStats


@dataclass
class ProtectionCategory:
    """Una categoría fusionada de `protection_advantage` y sus Celdas."""

    label: str
    lo: int
    hi: int
    n_total: int
    cells: dict[str, CellStats] = field(default_factory=dict)


@dataclass
class SegmentB:
    """Un conjunto de jugadas (total o un valor de segmentación)."""

    label: str
    n: int
    comparisons: list[MetricComparison] = field(default_factory=list)
    protection: list[ProtectionCategory] = field(default_factory=list)


@dataclass
class SegmentationB:
    """Segmentación independiente por una variable."""

    name: str
    column: str
    excluded_null: int
    segments: list[SegmentB] = field(default_factory=list)


@dataclass
class BlockB:
    """Resultado del Bloque B."""

    n_plays: int
    n_valid: int
    excluded_null_blitz: int
    excluded_by_metric: dict[str, int]
    protection_bins: list[dict]
    protection_merges: list[str]
    total: SegmentB
    segmentations: list[SegmentationB] = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_native(self)


def _category_label(lo: int, hi: int) -> str:
    return str(lo) if lo == hi else f"{lo} a {hi}"


def _diff_b(x1: np.ndarray, x0: np.ndarray, kind: str) -> DiffStats:
    """Diferencia blitz menos no blitz con las reglas del Bloque B."""
    if kind == "binary":
        d = diff_props_ci(int(round(x1.sum())), int(x1.size), int(round(x0.sum())), int(x0.size))
    else:
        d = diff_means_ci(x1, x0)
    if d.diff is None:
        return d
    if x1.size < MIN_N or x0.size < MIN_N:
        d.lo = d.hi = None
        d.flags = [f for f in d.flags if f != FLAG_UNAVAILABLE] + [FLAG_INSUFFICIENT]
    elif kind == "continuous" and (float(x1.std(ddof=1)) == 0.0 and float(x0.std(ddof=1)) == 0.0):
        d.lo = d.hi = None
        d.flags.append(FLAG_NOT_COMPUTABLE)
    return d


def _segment_b(df: pd.DataFrame, label: str, bins: list[tuple[int, int]]) -> SegmentB:
    """Calcula comparaciones blitz y categorías de protección dentro de `df`."""
    seg = SegmentB(label=label, n=int(len(df)))
    for metric, kind in BLOCK_B_METRICS:
        ok = df[df[metric].notna()]
        g1 = _clean(ok.loc[ok["_blitz"] == 1, metric])
        g0 = _clean(ok.loc[ok["_blitz"] == 0, metric])
        seg.comparisons.append(MetricComparison(
            metric=metric, kind=kind, excluded_null=int(len(df) - len(ok)),
            blitz=summarize_cell(g1, kind, "blitz", "B"),
            no_blitz=summarize_cell(g0, kind, "no blitz", "B"),
            diff=_diff_b(g1, g0, kind),
        ))
    prot = df[df["_prot"].notna()]
    for lo, hi in bins:
        sub = prot[(prot["_prot"] >= lo) & (prot["_prot"] <= hi)]
        cat = ProtectionCategory(
            label=_category_label(lo, hi), lo=lo, hi=hi, n_total=int(len(sub)),
        )
        for metric, kind in BLOCK_B_METRICS:
            cat.cells[metric] = summarize_cell(sub[metric], kind, cat.label, "B")
        seg.protection.append(cat)
    return seg


def build_block_b(master: pd.DataFrame, run: RunReport | None = None) -> BlockB:
    """Bloque B: blitz (`is_blitz` == 1) contra no blitz y bolsillo.

    Universo: jugadas con `is_blitz` no nulo. Cada métrica excluye (y declara)
    sus nulos sin afectar a las demás. Los límites de `protection_advantage`
    se calculan una vez sobre el total con ese valor no nulo y se aplican a
    toda segmentación. `pff_passCoverage` y `offenseFormation` segmentan de
    forma independiente; las jugadas con nulo en la variable se excluyen y se
    cuentan.
    """
    run = run if run is not None else RunReport()
    missing = [c for c in BLOCK_B_REQUIRED if c not in master.columns]
    if missing:
        raise PipelineError(f"Faltan columnas para el Bloque B: {missing}")

    n_plays = int(len(master))
    d = master.copy()
    d["_blitz"] = pd.to_numeric(d["is_blitz"], errors="coerce")
    d["_prot"] = pd.to_numeric(d["protection_advantage"], errors="coerce")
    for metric, _ in BLOCK_B_METRICS:
        d[metric] = pd.to_numeric(d[metric], errors="coerce")
        d.loc[~np.isfinite(d[metric].astype("float64")), metric] = np.nan

    # Límites de protection_advantage: una vez, sobre el total con valor no nulo.
    prot_all = d["_prot"].dropna().round().astype("int64")
    counts = prot_all.value_counts().sort_index()
    bins = merge_small_bins(counts)
    bin_info, merges = [], []
    for lo, hi in bins:
        n_cat = int(counts[(counts.index >= lo) & (counts.index <= hi)].sum())
        flags = [FLAG_INSUFFICIENT] if n_cat < MIN_N else []
        bin_info.append({
            "label": _category_label(lo, hi), "min": lo, "max": hi, "n": n_cat, "flags": flags,
        })
        if lo != hi:
            merges.append(f"Valores {lo} a {hi} fusionados en una categoría (n = {n_cat}).")
    d["_prot"] = d["_prot"].round()

    d = d[d["_blitz"].isin([0, 1])]
    n_valid = int(len(d))
    excluded = n_plays - n_valid
    run.add("block_b_excluded_null_blitz", excluded)

    total = _segment_b(d, "Total", bins)
    by_metric = {c.metric: c.excluded_null for c in total.comparisons}
    for metric, n_ex in by_metric.items():
        run.add(f"block_b_excluded_null_{metric}", n_ex)

    block = BlockB(
        n_plays=n_plays, n_valid=n_valid, excluded_null_blitz=excluded,
        excluded_by_metric=by_metric, protection_bins=bin_info,
        protection_merges=merges, total=total,
    )

    for name, column in (("coverage", "pff_passCoverage"), ("formation", "offenseFormation")):
        key = d[column]
        n_null = int(key.isna().sum())
        run.add(f"block_b_excluded_null_{name}", n_null)
        seg = SegmentationB(name=name, column=column, excluded_null=n_null)
        for v in sorted(key.dropna().unique(), key=str):
            seg.segments.append(_segment_b(d[key == v], str(v), bins))
        block.segmentations.append(seg)
    return block


# ---------------------------------------------------------------------------
# Reporte (tarea 5.5)
# ---------------------------------------------------------------------------

REPORT_PATH = OUTPUT_DIR / "COACH_INSIGHTS.md"

LIMITATIONS = (
    "Solo hay jugadas de pase (dropbacks); no se describen jugadas de carrera.",
    "Los datos cubren 8 semanas de la temporada 2021.",
    "No hay EPA; el éxito se mide con `is_success` a partir de down y distancia.",
    "El mérito táctico usa `prePenaltyPlayResult`, que ignora el efecto de castigos.",
)

_NA = "—"


def _f(v) -> str:
    """Formatea un número a 3 decimales; nulo como guion."""
    r = _r3(v)
    if r is None:
        return _NA
    return str(r) if isinstance(r, int) else f"{r:.3f}"


def _ci(lo, hi) -> str:
    if lo is None or hi is None:
        return _NA
    return f"[{_f(lo)}, {_f(hi)}]"


def _flags(flags) -> str:
    return ", ".join(flags) if flags else _NA


def _cell_text(s) -> str:
    """Escapa barras verticales para no romper las tablas Markdown."""
    return str(s).replace("|", "\\|").replace("\n", " ")


def _table(header: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(_cell_text(c) for c in r) + " |" for r in rows]
    return out


def _count_nonnull(master: pd.DataFrame, col: str) -> int:
    return int(master[col].notna().sum()) if col in master.columns else 0


def _coverage_lines(master: pd.DataFrame, run: RunReport) -> list[str]:
    n_valid = int(len(master))
    dt_ok = 0
    if "frame_dt_ok" in master.columns:
        dt_ok = int((pd.to_numeric(master["frame_dt_ok"], errors="coerce") == 1).sum())
    ok = int(run.counts.get("tracking_ok", 0))
    err = int(run.counts.get("tracking_error", 0))
    rows = [
        ["Jugadas válidas", str(n_valid)],
        ["`time_to_throw` no nulo", str(_count_nonnull(master, "time_to_throw"))],
        ["`min_rusher_dist_at_throw` no nulo", str(_count_nonnull(master, "min_rusher_dist_at_throw"))],
        ["`lb_bite_yards` no nulo", str(_count_nonnull(master, "lb_bite_yards"))],
        ["`frame_dt_ok` = 1", str(dt_ok)],
        ["Archivos de tracking procesados (ok)", str(ok)],
        ["Archivos de tracking con error", str(err)],
    ]
    return ["## Resumen de cobertura", ""] + _table(["Concepto", "Valor"], rows) + [""]


def _diff_row(label: str, d: DiffStats, unit: str) -> list[str]:
    return [label, str(d.n1), str(d.n0), _f(d.diff), _ci(d.lo, d.hi), unit, _flags(d.flags)]


def _render_block_a(a: BlockA) -> list[str]:
    out = [
        "## Bloque A: play action", "",
        "Diferencia = play action (1) menos sin play action (0). "
        "La tasa de éxito va en puntos porcentuales; las otras diferencias, en yardas.", "",
        f"- Jugadas totales: {a.n_plays}",
        f"- Jugadas con `pff_playAction` válido: {a.n_valid}",
        f"- Excluidas por `pff_playAction` nulo: {a.excluded_null_play_action}", "",
    ]
    header = ["Celda", "n play action", "n sin play action", "Diferencia", "IC95", "Unidad", "Etiquetas"]

    def cell_rows(c: ComparisonCell) -> list[list[str]]:
        rows = []
        for name, d, unit in (
            ("prePenaltyPlayResult", c.pre_penalty, "yardas"),
            ("playResult", c.play_result, "yardas"),
            ("tasa de éxito", c.success_pp, "pp"),
        ):
            r = _diff_row(f"{c.label}: {name}", d, unit)
            r[-1] = _flags(list(dict.fromkeys(c.flags + d.flags)))
            rows.append(r)
        return rows

    out += ["### Total", ""] + _table(header, cell_rows(a.total)) + [""]
    for bd in a.breakdowns:
        out += [f"### Desglose por `{bd.column}` ({bd.name})", ""]
        out.append(f"Jugadas excluidas por valor nulo en `{bd.column}`: {bd.excluded_null}")
        if bd.edges is not None:
            if bd.edges:
                edges = ", ".join(f"{e:.2f}" for e in bd.edges)
                out.append(
                    f"Bordes de rango ({bd.unit}): {edges}. Intervalos cerrados a la izquierda, "
                    "[inferior, superior). Valores altos indican que los linebackers avanzaron "
                    "hacia la línea de golpeo (mordieron)."
                )
            else:
                out.append("Sin valores de `lb_bite_yards`: no hay rangos.")
        out.append("")
        rows = [r for c in bd.cells for r in cell_rows(c)]
        if rows:
            out += _table(header, rows) + [""]
        else:
            out += ["Sin celdas.", ""]
    return out


def _cellstats_row(c: CellStats) -> list[str]:
    return [str(c.n), _f(c.mean), _ci(c.mean_lo, c.mean_hi)]


def _render_segment_b(seg: SegmentB, level: str) -> list[str]:
    out = [f"{level} {seg.label} (n = {seg.n})", "", "Blitz contra no blitz (diferencia = blitz menos no blitz):", ""]
    header = [
        "Métrica", "Excluidas por nulo", "n blitz", "Media blitz", "IC95 blitz",
        "n no blitz", "Media no blitz", "IC95 no blitz", "Diferencia", "IC95 diferencia", "Etiquetas",
    ]
    rows = []
    for m in seg.comparisons:
        fl = list(dict.fromkeys(m.blitz.flags + m.no_blitz.flags + m.diff.flags))
        rows.append([
            f"{m.metric} ({m.kind})", str(m.excluded_null),
            str(m.blitz.n), _f(m.blitz.mean), _ci(m.blitz.mean_lo, m.blitz.mean_hi),
            str(m.no_blitz.n), _f(m.no_blitz.mean), _ci(m.no_blitz.mean_lo, m.no_blitz.mean_hi),
            _f(m.diff.diff), _ci(m.diff.lo, m.diff.hi), _flags(fl),
        ])
    out += _table(header, rows) + [""]
    if seg.protection:
        out += ["Por categoría de `protection_advantage`:", ""]
        header = ["Categoría", "n total", "Métrica", "n", "Media o proporción", "IC95", "Etiquetas"]
        rows = []
        for cat in seg.protection:
            for metric, _ in BLOCK_B_METRICS:
                c = cat.cells[metric]
                rows.append([
                    cat.label, str(cat.n_total), metric, str(c.n), _f(c.mean),
                    _ci(c.mean_lo, c.mean_hi), _flags(c.flags),
                ])
        out += _table(header, rows) + [""]
    return out


def _render_block_b(b: BlockB) -> list[str]:
    out = [
        "## Bloque B: blitz y bolsillo", "",
        "Blitz = 5 o más rushers. Cada métrica excluye solo sus propios nulos.", "",
        f"- Jugadas totales: {b.n_plays}",
        f"- Jugadas con `is_blitz` válido: {b.n_valid}",
        f"- Excluidas por `is_blitz` nulo: {b.excluded_null_blitz}", "",
        "Jugadas excluidas por nulo en cada métrica (conjunto total):", "",
    ]
    out += _table(["Métrica", "Excluidas"], [[k, str(v)] for k, v in b.excluded_by_metric.items()]) + [""]
    out += ["### Categorías de `protection_advantage`", "",
            "Límites calculados una vez sobre el total y aplicados a toda segmentación.", ""]
    rows = [
        [d["label"], str(d["min"]), str(d["max"]), str(d["n"]), _flags(d["flags"])]
        for d in b.protection_bins
    ]
    out += _table(["Categoría", "Mínimo", "Máximo", "n", "Etiquetas"], rows) if rows else ["Sin categorías."]
    out.append("")
    if b.protection_merges:
        out += ["Fusiones:", ""] + [f"- {m}" for m in b.protection_merges] + [""]
    else:
        out += ["Sin fusiones.", ""]
    out += _render_segment_b(b.total, "###")
    for sg in b.segmentations:
        out += [f"### Segmentación por `{sg.column}` ({sg.name})", "",
                f"Jugadas excluidas por valor nulo en `{sg.column}`: {sg.excluded_null}", ""]
        if not sg.segments:
            out += ["Sin segmentos.", ""]
        for seg in sg.segments:
            out += _render_segment_b(seg, "####")
    return out


def _render_annex(run: RunReport) -> list[str]:
    out = ["## Anexo de ejecución", "", "### Conteos", ""]
    if run.counts:
        out += _table(["Concepto", "Valor"], [[k, str(v)] for k, v in sorted(run.counts.items())])
    else:
        out.append("Sin conteos registrados.")
    out += ["", "### Avisos", ""]
    if run.warnings:
        out += [f"- {w}" for w in run.warnings]
    else:
        out.append("Sin avisos.")
    out.append("")
    return out


def render_report(
    master: pd.DataFrame, block_a: BlockA, block_b: BlockB, run: RunReport | None = None
) -> str:
    """Genera el texto Markdown completo del reporte, sin tocar disco.

    Secciones: resumen de cobertura, limitaciones, Bloque A, Bloque B y anexo
    de ejecución. Los valores decimales se muestran a 3 decimales.
    """
    run = run if run is not None else RunReport()
    lines = ["# Coach Insights", ""]
    lines += _coverage_lines(master, run)
    lines += ["## Limitaciones", ""] + [f"- {t}" for t in LIMITATIONS] + [""]
    lines += _render_block_a(block_a)
    lines += _render_block_b(block_b)
    lines += _render_annex(run)
    return "\n".join(lines).rstrip("\n") + "\n"


def write_report_atomic(text: str, path: Path | str = REPORT_PATH) -> None:
    """Escribe el reporte a un temporal y lo mueve con `os.replace`.

    Si algo falla se borra el temporal, se conserva el reporte previo y se
    lanza `PipelineError` con la ruta y la causa.
    """
    path = Path(path)
    tmp_name: str | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        os.replace(tmp_name, path)
        tmp_name = None
    except Exception as exc:
        raise PipelineError(
            f"No se pudo escribir el reporte en {path}: {type(exc).__name__}: {exc}"
        ) from exc
    finally:
        if tmp_name is not None:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Tabla maestra y persistencia (tarea 6.1)
# ---------------------------------------------------------------------------

KEYS = ["gameId", "playId"]
MASTER_STEM = "plays_enriched"
PFF_FEATURE_COLUMNS = (
    "n_rushers", "n_blockers", "protection_advantage",
    "is_blitz", "any_pressure", "any_beaten",
)


def build_master(
    features: pd.DataFrame, tracking: pd.DataFrame | None, run: RunReport | None = None
) -> pd.DataFrame:
    """Left join de features con el agregado de tracking por (gameId, playId).

    Orden de columnas: features, tracking sin la llave y `has_tracking`.
    Registra en el Log y en `run` las jugadas con nulos por módulo ausente.
    """
    run = run if run is not None else RunReport()
    feats = features.reset_index(drop=True)
    if tracking is None or len(tracking.columns) == 0:
        trk = pd.DataFrame(columns=KEYS)
    else:
        trk = tracking.drop_duplicates(KEYS).copy()
    trk_cols = [c for c in trk.columns if c not in KEYS]
    trk = trk.assign(has_tracking=True)

    master = feats.merge(trk, on=KEYS, how="left", validate="one_to_one")
    master["has_tracking"] = master["has_tracking"].eq(True)
    master = master[list(feats.columns) + trk_cols + ["has_tracking"]]

    n_no_tracking = int((~master["has_tracking"]).sum())
    run.add("master_plays_without_tracking", n_no_tracking)
    pff_cols = [c for c in PFF_FEATURE_COLUMNS if c in master.columns]
    n_no_pff = int(master[pff_cols].isna().all(axis=1).sum()) if pff_cols else 0
    run.add("master_plays_without_pff", n_no_pff)
    logger.info(
        "Tabla maestra: %d jugadas; %d sin tracking (nulos en columnas de tracking); "
        "%d sin PFF (nulos en columnas PFF).",
        len(master), n_no_tracking, n_no_pff,
    )
    return master


def detect_format() -> tuple[str, str]:
    """Elige el formato de salida sin importar `pyarrow`."""
    if importlib.util.find_spec("pyarrow") is not None:
        return "parquet", "pyarrow presente en .venv"
    return "csv", "pyarrow ausente en .venv"


def save_master(
    master: pd.DataFrame, out_dir: Path | str = OUTPUT_DIR, run: RunReport | None = None
) -> Path:
    """Guarda la tabla maestra de forma atómica y devuelve la ruta final."""
    out_dir = Path(out_dir)
    fmt, reason = detect_format()
    logger.info("Formato de la tabla maestra: %s (%s).", fmt, reason)
    if run is not None:
        run.add(f"master_format_{fmt}")
    final = out_dir / f"{MASTER_STEM}.{fmt}"
    tmp = out_dir / f".{MASTER_STEM}.{fmt}.tmp"
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        if fmt == "parquet":
            master.to_parquet(tmp, index=False)
        else:
            master.to_csv(tmp, index=False)
        os.replace(tmp, final)
    except Exception as exc:
        raise PipelineError(
            f"No se pudo escribir la tabla maestra en {final}: {type(exc).__name__}: {exc}"
        ) from exc
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass
    return final


def _read_master_file(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path, float_precision="round_trip")


def load_master(out_dir: Path | str = OUTPUT_DIR) -> pd.DataFrame | None:
    """Lee `plays_enriched.parquet` o `.csv`; devuelve None si no existe ninguno."""
    out_dir = Path(out_dir)
    for ext in ("parquet", "csv"):
        path = out_dir / f"{MASTER_STEM}.{ext}"
        if path.exists():
            return _read_master_file(path)
    return None


def verify_roundtrip(master: pd.DataFrame, path: Path | str) -> None:
    """Relee el archivo y compara filas, columnas en orden e `is_success`."""
    path = Path(path)
    try:
        back = _read_master_file(path)
    except Exception as exc:
        raise PipelineError(
            f"No se pudo releer la tabla maestra en {path}: {type(exc).__name__}: {exc}"
        ) from exc
    if len(back) != len(master):
        raise PipelineError(
            f"Ida y vuelta fallida en {path}: {len(master)} filas guardadas, {len(back)} leídas."
        )
    if list(back.columns) != list(master.columns):
        raise PipelineError(
            f"Ida y vuelta fallida en {path}: las columnas o su orden difieren."
        )
    if "is_success" in master.columns:
        a = master["is_success"].to_numpy()
        b = back["is_success"].to_numpy()
        if not np.array_equal(a, b):
            n_diff = int((a != b).sum())
            raise PipelineError(
                f"Ida y vuelta fallida en {path}: {n_diff} valores de is_success difieren."
            )


# ---------------------------------------------------------------------------
# Orquestación del pipeline (tarea 6.2)
# ---------------------------------------------------------------------------


def run_pipeline(
    out_dir: Path | str = OUTPUT_DIR,
    data_dir: Path | str | None = None,
    write: bool = True,
    game_ids=None,
) -> tuple[pd.DataFrame, RunReport]:
    """Ejecuta features, tracking, tabla maestra y (si `write`) su persistencia.

    `game_ids` limita los archivos de tracking procesados (subconjuntos o pruebas).
    Con `write=False` todo ocurre en memoria y no se toca el disco.
    """
    # Imports locales: evitan ciclos y mantienen la importación sin efectos.
    from src.features import DATA_DIR, build_features, load_base_tables
    from src.tracking_metrics import build_context, compute_tracking_metrics

    data_dir = Path(data_dir) if data_dir is not None else DATA_DIR
    run = RunReport()

    tables = load_base_tables(data_dir)
    features = build_features(tables, run)
    ctx = build_context(tables, features)
    tracking, counts = compute_tracking_metrics(
        data_dir / "tracking", ctx, run, game_ids=game_ids
    )
    for key in ("ok", "error", "attempted"):
        run.counts[f"tracking_files_{key}"] = int(counts[key])

    master = build_master(features, tracking, run)
    if write:
        path = save_master(master, out_dir, run)
        verify_roundtrip(master, path)
    return master, run


def load_or_build_master(
    out_dir: Path | str = OUTPUT_DIR,
    data_dir: Path | str | None = None,
    game_ids=None,
) -> pd.DataFrame:
    """Lee `outputs/plays_enriched.*` o calcula la tabla en memoria (sin escribir)."""
    master = load_master(out_dir)
    if master is not None:
        return master
    master, _ = run_pipeline(out_dir, data_dir, write=False, game_ids=game_ids)
    return master


def main(argv=None) -> int:
    """Corre el pipeline y escribe el reporte. Devuelve 0 si todo sale bien, 1 si no."""
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    try:
        master, run = run_pipeline()
        block_a = build_block_a(master, run)
        block_b = build_block_b(master, run)
        text = render_report(master, block_a, block_b, run)
        write_report_atomic(text)
    except PipelineError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - se informa y se devuelve código 1
        print(f"Error inesperado: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
