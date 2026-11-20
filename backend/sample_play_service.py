"""GET /api/sample-play: selección de una jugada real y su tracking."""
from __future__ import annotations

import logging
import random
import re
from typing import Mapping

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Request

from backend import config, tracking
from backend.situation import SituationError, parse_situation, subset_mask
from backend.store import PlaysStore, require_store

log = logging.getLogger("backend.sample_play")

router = APIRouter()

FOCUS_VALUES = ("bite", "pa_fallida", "blitz_exitoso")
MAX_EXCLUDE = 100
MAX_OPEN_ATTEMPTS = 20
MAX_RANGE_DISCARDS = 5
BITE_THRESHOLD = 1.16
_ID_RE = re.compile(r"^\d+-\d+$")

NO_CANDIDATES_MSG = "No hay jugadas con tracking para la situación elegida."
UNUSABLE_MSG = "No hay jugada con tracking utilizable."

# Generador inyectable (las pruebas lo reemplazan).
_rng = random.Random()


def set_rng(rng: random.Random) -> None:
    global _rng
    _rng = rng


# --------------------------------------------------------------------------
# Selección (pura)
# --------------------------------------------------------------------------
def parse_exclude(raw: str | None) -> list[str]:
    """Lista de ``play_id`` válidos. Más de 100 elementos lanza SituationError."""
    if raw is None or raw.strip() == "":
        return []
    items = [t.strip() for t in raw.split(",") if t.strip() != ""]
    if len(items) > MAX_EXCLUDE:
        raise SituationError(
            f"Parámetro(s) inválido(s): exclude (máximo {MAX_EXCLUDE} identificadores).",
            ["exclude"],
        )
    return [t for t in items if _ID_RE.match(t)]


def candidate_pool(sub: pd.DataFrame) -> pd.DataFrame:
    """Jugadas del Subset con tracking y ``snap_frameId``/``res_frameId`` no nulos (8.1)."""
    m = sub["has_tracking"].astype(bool) & sub["snap_frameId"].notna() & sub["res_frameId"].notna()
    if config.SAMPLE_PLAY_IDS is not None:
        m &= sub["play_id"].isin(config.SAMPLE_PLAY_IDS)
    return sub.loc[m]


def preferred_mask(pool: pd.DataFrame, focus: str | None) -> pd.Series:
    pa = pool["pff_playAction"] == 1
    ok = pool["is_success"] == 1
    if focus == "bite":
        return pa & ok & (pool["lb_bite_yards"] >= BITE_THRESHOLD)
    if focus == "pa_fallida":
        return pa & (pool["is_success"] == 0)
    if focus == "blitz_exitoso":
        return (pool["is_blitz"] == 1) & ok
    bite = pa & ok & (pool["lb_bite_yards"] >= BITE_THRESHOLD)
    return bite | ((pool["is_blitz"] == 1) & (pool["any_pressure"] == 1))


def order_candidates(
    pool: pd.DataFrame,
    focus: str | None,
    exclude,
    rng: random.Random,
) -> list[tuple[int, bool]]:
    """Orden de prueba (A6): pref\\exc, resto\\exc, pref, resto.

    Devuelve ``[(índice de fila, preferred)]`` con cada grupo barajado.
    """
    if len(pool) == 0:
        return []
    pref = preferred_mask(pool, focus).fillna(False).to_numpy(dtype=bool)
    exc = pool["play_id"].isin(set(exclude)).to_numpy(dtype=bool)
    idx = list(pool.index)
    groups = [
        [i for i, p, e in zip(idx, pref, exc) if p and not e],
        [i for i, p, e in zip(idx, pref, exc) if not p and not e],
        [i for i, p, e in zip(idx, pref, exc) if p and e],
        [i for i, p, e in zip(idx, pref, exc) if not p and e],
    ]
    out: list[tuple[int, bool]] = []
    is_pref = dict(zip(idx, pref))
    for g in groups:
        g = list(g)
        rng.shuffle(g)
        out.extend((i, bool(is_pref[i])) for i in g)
    return out


# --------------------------------------------------------------------------
# Construcción de la respuesta
# --------------------------------------------------------------------------
def _py(v):
    """Valor JSON-seguro: NaN/NA -> None, numpy -> Python."""
    if v is None or v is pd.NA:
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        f = float(v)
        return None if np.isnan(f) else f
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return v


def _int_or_none(v):
    v = _py(v)
    return None if v is None else int(v)


def play_info(row: pd.Series) -> dict:
    return {
        "id": str(row["play_id"]),
        "gameId": int(row["gameId"]),
        "playId": int(row["playId"]),
        "week": _int_or_none(row.get("week")),
        "offense": _py(row.get("possessionTeam")),
        "defense": _py(row.get("defensiveTeam")),
        "down": _int_or_none(row.get("down")),
        "yards_to_go": _int_or_none(row.get("yardsToGo")),
        "coverage": _py(row.get("pff_passCoverage")),
        "formation": _py(row.get("offenseFormation")),
        "play_action": _int_or_none(row.get("pff_playAction")),
        "is_blitz": _int_or_none(row.get("is_blitz")),
        "any_pressure": _int_or_none(row.get("any_pressure")),
        "is_success": _int_or_none(row.get("is_success")),
        "lb_bite_yards": _py(row.get("lb_bite_yards")),
        "min_rusher_dist_at_throw": _py(row.get("min_rusher_dist_at_throw")),
        "time_to_throw": _py(row.get("time_to_throw")),
    }


def _r2(v):
    v = _py(v)
    return None if v is None else round(v, 2)


def build_tracking_payload(
    clipped: pd.DataFrame, roles: pd.DataFrame
) -> tuple[list[int], list[dict], list[dict]]:
    """``(frames, players, ball)`` a partir del tracking normalizado y recortado."""
    frames = sorted(int(f) for f in clipped["frameId"].unique())
    ball_df = clipped[clipped["team"].astype(str) == "football"]
    ball = [
        {"frameId": int(r.frameId), "x_norm": _r2(r.x_norm), "y_norm": _r2(r.y_norm)}
        for r in ball_df.sort_values("frameId").itertuples(index=False)
    ]
    people = clipped[(clipped["team"].astype(str) != "football") & clipped["nflId"].notna()]
    by_player = {int(k): g.sort_values("frameId") for k, g in people.groupby("nflId")}
    players: list[dict] = []
    for r in roles.itertuples(index=False):
        g = by_player.get(int(r.nflId))
        if g is None:
            continue
        track = [
            {
                "frameId": int(t.frameId),
                "x_norm": _r2(t.x_norm),
                "y_norm": _r2(t.y_norm),
                "s": _py(t.s),
                "a": _py(t.a),
            }
            for t in g.itertuples(index=False)
        ]
        players.append({
            "nflId": int(r.nflId),
            "role": r.role,
            "position": _py(r.position),
            "label": r.label,
            "side": r.side,
            "is_lb": bool(r.is_lb),
            "track": track,
        })
    return frames, players, ball


def _load_play(row: pd.Series, st: PlaysStore) -> dict:
    """Lee y arma una jugada. Lanza FileNotFoundError o SinRango."""
    game_id, play_id = int(row["gameId"]), int(row["playId"])
    path = config.TRACKING_DIR / f"tracking_{game_id}.csv"
    raw = tracking.read_play_tracking(path, game_id, play_id)
    if raw.empty:
        raise tracking.SinRango("la jugada no tiene filas en el tracking")
    snap, res, warns = tracking.find_range(raw, row.get("snap_frameId"), row.get("res_frameId"))
    norm = tracking.normalize_xy(raw)
    clipped = tracking.clip_range(norm, snap, res)
    if clipped.empty:
        raise tracking.SinRango("sin frames en el rango snap..pass_forward")

    try:
        pff, officials = tracking.load_role_tables(config.DATA_DIR, st.df[["gameId", "playId"]])
    except FileNotFoundError as exc:
        raise _RoleTablesMissing(str(exc)) from exc
    pff_play = pff[(pff["gameId"] == game_id) & (pff["playId"] == play_id)]
    people = clipped[(clipped["team"].astype(str) != "football") & clipped["nflId"].notna()]
    team_map = {"home": row["homeTeamAbbr"], "away": row["visitorTeamAbbr"]}
    roles = tracking.assign_roles(people, pff_play, officials, row["possessionTeam"], team_map)
    frames, players, ball = build_tracking_payload(clipped, roles)
    return {
        "snap_frame": snap,
        "pass_forward_frame": res,
        "frames": frames,
        "players": players,
        "ball": ball,
        "warnings": warns,
    }


class _RoleTablesMissing(Exception):
    pass


# --------------------------------------------------------------------------
# Servicio
# --------------------------------------------------------------------------
def select_and_load(
    st: PlaysStore,
    f,
    focus: str | None,
    exclude: list[str],
    rng: random.Random | None = None,
) -> dict:
    rng = rng or _rng
    df = st.df
    sub = df[subset_mask(df, f)]
    pool = candidate_pool(sub)
    if len(pool) == 0:
        raise HTTPException(status_code=404, detail=NO_CANDIDATES_MSG)

    order = order_candidates(pool, focus, exclude, rng)
    opens = 0
    discards = 0
    any_file = False
    for idx, preferred in order:
        if opens >= MAX_OPEN_ATTEMPTS:
            break
        opens += 1
        row = df.loc[idx]
        try:
            data = _load_play(row, st)
        except FileNotFoundError:
            continue
        except _RoleTablesMissing as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Faltan archivos de datos de jugadores en {config.DATA_DIR}: {exc}",
            ) from exc
        except tracking.SinRango as exc:
            any_file = True
            discards += 1
            log.warning("Jugada %s descartada: %s", row["play_id"], exc)
            if discards >= MAX_RANGE_DISCARDS:
                break
            continue
        data.pop("warnings", None)
        return {"preferred": bool(preferred), "play": play_info(row), **data}

    if not any_file:
        raise HTTPException(
            status_code=503,
            detail=(
                "No se encontró el tracking de las jugadas candidatas. "
                f"Ruta esperada del directorio de tracking: {config.TRACKING_DIR}"
            ),
        )
    raise HTTPException(status_code=503, detail=UNUSABLE_MSG)


def _parse_params(raw: Mapping[str, str], st: PlaysStore):
    """Valida situación, focus y exclude juntos; todos los inválidos se nombran."""
    invalid_names: list[str] = []
    details: list[str] = []
    f = None
    try:
        f = parse_situation(raw, st)
    except SituationError as exc:
        invalid_names += exc.invalid
        details.append(exc.detail.removeprefix("Parámetro(s) inválido(s): ").rstrip("."))
    focus = raw.get("focus")
    if focus is None or focus == "":
        focus = None
    elif focus not in FOCUS_VALUES:
        invalid_names.append("focus")
        details.append(f"focus (valor '{focus}'; use bite, pa_fallida o blitz_exitoso)")
        focus = None
    exclude: list[str] = []
    try:
        exclude = parse_exclude(raw.get("exclude"))
    except SituationError as exc:
        invalid_names += exc.invalid
        details.append(exc.detail.removeprefix("Parámetro(s) inválido(s): ").rstrip("."))
    if invalid_names:
        raise SituationError(f"Parámetro(s) inválido(s): {', '.join(details)}.", invalid_names)
    return f, focus, exclude


@router.get("/sample-play")
def get_sample_play(request: Request, st: PlaysStore = Depends(require_store)) -> dict:
    f, focus, exclude = _parse_params(dict(request.query_params), st)
    return select_and_load(st, f, focus, exclude)
