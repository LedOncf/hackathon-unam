"""Recommend_Service: estadística de grupos, tablas de física y diferencias."""
from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from backend.config import MIN_N
from backend.situation import SituationFilter, subset_mask
from backend.stats import mean_or_none, newcombe_diff_pp, r1, r2, r3, wilson_pct

INSUFFICIENT_LABEL = "Muestra insuficiente (n < 30)"

BITE_EDGES = (0.10, 0.69, 1.16)
BITE_ROWS = [
    ("< 0.10", None, 0.10),
    ("0.10 a 0.69", 0.10, 0.69),
    ("0.69 a 1.16", 0.69, 1.16),
    (">= 1.16", 1.16, None),
]
PROT_CATEGORIES = ["-2 a -1", "0", "1", "2", "3 a 6"]


def _flags(n: int) -> dict:
    insufficient = n < MIN_N
    return {"insufficient": insufficient, "label": INSUFFICIENT_LABEL if insufficient else None}


def _mean_stat(series: pd.Series) -> dict:
    m, n_used = mean_or_none(series, 2)
    return {"mean": m, "n_used": n_used}


def _rate_ci(k: int, n: int) -> tuple[float | None, list[float] | None]:
    if n <= 0:
        return None, None
    ci = wilson_pct(k, n)
    return r1(100.0 * k / n), (list(ci) if ci else None)


def _pa_group(g: pd.DataFrame) -> dict:
    n = int(len(g))
    k = int(g["is_success"].sum()) if n else 0
    rate, ci = _rate_ci(k, n)
    return {
        "n": n,
        "successes": k,
        "success_rate": rate,
        "ci": ci,
        "mean_yards": mean_or_none(g["prePenaltyPlayResult"], 2)[0],
        "lb_bite": _mean_stat(g["lb_bite_yards"]),
        "unrounded_yards": mean_or_none(g["prePenaltyPlayResult"], None)[0],
        **_flags(n),
    }


def _blitz_group(g: pd.DataFrame) -> dict:
    n = int(len(g))
    k = int(g["is_success"].sum()) if n else 0
    rate, ci = _rate_ci(k, n)
    return {
        "n": n,
        "success_rate": rate,
        "ci": ci,
        "any_pressure_pct": r1(100.0 * g["any_pressure"].mean()) if n else None,
        "time_to_throw": _mean_stat(g["time_to_throw"]),
        "min_rusher_dist": _mean_stat(g["min_rusher_dist_at_throw"]),
        **_flags(n),
    }


def _diff(a: float | None, b: float | None, nd: int) -> float | None:
    if a is None or b is None:
        return None
    return r1(a - b) if nd == 1 else r2(a - b)


def _effect(g1: pd.DataFrame, g0: pd.DataFrame) -> tuple[float | None, list[float] | None]:
    if len(g1) == 0 or len(g0) == 0:
        return None, None
    res = newcombe_diff_pp(int(g1["is_success"].sum()), len(g1), int(g0["is_success"].sum()), len(g0))
    if res is None:
        return None, None
    return res[0], [res[1], res[2]]


def _public(group: dict) -> dict:
    return {k: v for k, v in group.items() if k != "unrounded_yards"}


def _lb_bite_table(sub: pd.DataFrame) -> list[dict]:
    rows = []
    valid = sub[sub["bite_bin"] >= 0]
    for i, (name, lo, hi) in enumerate(BITE_ROWS):
        seg = valid[valid["bite_bin"] == i]
        pa = seg[seg["pff_playAction"] == 1]
        tr = seg[seg["pff_playAction"] == 0]
        rows.append({
            "range": name, "lo": lo, "hi": hi,
            "n": int(len(seg)), "n_pa": int(len(pa)), "n_trad": int(len(tr)),
            "pa_success_rate": r3(pa["is_success"].mean()) if len(pa) else None,
            "trad_success_rate": r3(tr["is_success"].mean()) if len(tr) else None,
            "pa_pressure_rate": r3(pa["any_pressure"].mean()) if len(pa) else None,
            "trad_pressure_rate": r3(tr["any_pressure"].mean()) if len(tr) else None,
            **_flags(len(seg)),
        })
    return rows


def _protection_table(sub: pd.DataFrame) -> list[dict]:
    rows = []
    for cat in PROT_CATEGORIES:
        seg = sub[sub["prot_cat"] == cat]
        n = int(len(seg))
        rows.append({
            "category": cat, "n": n,
            "any_pressure": r3(seg["any_pressure"].mean()) if n else None,
            "success_rate": r3(seg["is_success"].mean()) if n else None,
            **_flags(n),
        })
    return rows


def compute_blocks(df: pd.DataFrame, f: SituationFilter) -> dict:
    """Todo el contrato de /api/recommend salvo `verdict`."""
    sub = df[subset_mask(df, f)]
    pa_df = sub[sub["pff_playAction"] == 1]
    tr_df = sub[sub["pff_playAction"] == 0]
    bl_df = sub[sub["is_blitz"] == 1]
    sd_df = sub[sub["is_blitz"] == 0]

    pa, tr = _pa_group(pa_df), _pa_group(tr_df)
    pa_eff, pa_ci = _effect(pa_df, tr_df)
    eff_yards = (
        r2(pa["unrounded_yards"] - tr["unrounded_yards"])
        if pa["unrounded_yards"] is not None and tr["unrounded_yards"] is not None
        else None
    )

    bl, sd = _blitz_group(bl_df), _blitz_group(sd_df)
    bl_eff, bl_ci = _effect(bl_df, sd_df)
    pressure_pp = (
        r1(100.0 * (bl_df["any_pressure"].mean() - sd_df["any_pressure"].mean()))
        if len(bl_df) and len(sd_df) else None
    )
    ttt_b = mean_or_none(bl_df["time_to_throw"], None)[0]
    ttt_s = mean_or_none(sd_df["time_to_throw"], None)[0]
    mrd_b = mean_or_none(bl_df["min_rusher_dist_at_throw"], None)[0]
    mrd_s = mean_or_none(sd_df["min_rusher_dist_at_throw"], None)[0]

    return {
        "subset_n": int(len(sub)),
        "filter": asdict(f),
        "play_action": {
            "play_action": _public(pa), "traditional": _public(tr),
            "effect_pp": pa_eff, "effect_pp_ci": pa_ci, "effect_yards": eff_yards,
        },
        "blitz": {
            "blitz": bl, "standard": sd,
            "effect_pp": bl_eff, "effect_pp_ci": bl_ci,
            "pressure_pp": pressure_pp,
            "time_to_throw_diff": _diff(ttt_b, ttt_s, 2),
            "min_rusher_dist_diff": _diff(mrd_b, mrd_s, 2),
        },
        "physics": {
            "lb_bite_table": _lb_bite_table(sub),
            "protection_table": _protection_table(sub),
        },
    }


def build_recommendation(df: pd.DataFrame, f: SituationFilter) -> dict:
    """Respuesta completa de /api/recommend (incluye el Verdict)."""
    from backend.verdict import build_verdict  # import tardío: módulo de la tarea 4.2

    out = compute_blocks(df, f)
    pa_block, bl_block = out["play_action"], out["blitz"]
    out["verdict"] = build_verdict(
        subset_n=out["subset_n"],
        n_pa=pa_block["play_action"]["n"],
        n_trad=pa_block["traditional"]["n"],
        effect_pp=pa_block["effect_pp"],
        effect_pp_ci=pa_block["effect_pp_ci"],
        coverage=f.coverage,
        n_blitz=bl_block["blitz"]["n"],
        n_standard=bl_block["standard"]["n"],
        pressure_pp=bl_block["pressure_pp"],
    )
    return out
