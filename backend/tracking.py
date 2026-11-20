"""Lectura de tracking de una jugada, normalización, rango de frames y roles.

Las funciones son puras sobre DataFrames salvo ``read_play_tracking`` y los
cargadores perezosos de ``pffScoutingData.csv`` y ``players.csv``.
"""
from __future__ import annotations

import logging
import threading
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

CHUNK_ROWS = 100_000
TRACKING_COLUMNS = [
    "gameId", "playId", "nflId", "frameId", "team",
    "playDirection", "x", "y", "s", "a", "event",
]
_DTYPES = {
    "gameId": "int64", "playId": "int64", "nflId": "float64",
    "frameId": "int64", "team": "str", "playDirection": "str",
    "x": "float64", "y": "float64", "s": "float64", "a": "float64",
    "event": "str",
}
SNAP_EVENTS = {"ball_snap", "autoevent_ballsnap"}
PASS_EVENTS = {"pass_forward", "autoevent_passforward"}
# Mismo conjunto que src.tracking_metrics.LB_POSITIONS.
LB_POSITIONS = {"ILB", "MLB", "OLB", "LB"}

FIELD_LENGTH = 120.0
FIELD_WIDTH = 53.3

ROLES = ("QB", "Pass Route", "Pass Block", "Pass Rush", "Coverage", "LB")


class SinRango(Exception):
    """La jugada no tiene un rango de frames snap..pass_forward utilizable."""


# --------------------------------------------------------------------------
# Lectura
# --------------------------------------------------------------------------
def read_play_tracking(path, game_id: int, play_id: int) -> pd.DataFrame:
    """Lee un Tracking_File por bloques y devuelve solo las filas de la jugada.

    Lanza ``FileNotFoundError`` si el archivo no existe.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(str(path))
    parts: list[pd.DataFrame] = []
    reader = pd.read_csv(
        path, usecols=TRACKING_COLUMNS, dtype=_DTYPES, chunksize=CHUNK_ROWS
    )
    for chunk in reader:
        sel = chunk[(chunk["playId"] == int(play_id)) & (chunk["gameId"] == int(game_id))]
        if len(sel):
            parts.append(sel)
    if not parts:
        return pd.DataFrame({c: pd.Series(dtype=_DTYPES[c]) for c in TRACKING_COLUMNS})
    return pd.concat(parts, ignore_index=True)


# --------------------------------------------------------------------------
# Normalización
# --------------------------------------------------------------------------
def normalize_xy(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega ``x_norm`` y ``y_norm`` (ofensiva hacia +X).

    Igual que ``src.tracking_metrics.normalize_xy``: con ``left`` usa
    ``120 - x`` y ``53.3 - y``; excluye (con aviso) otros valores.
    """
    valid = df["playDirection"].isin(["left", "right"])
    if not valid.all():
        logger.warning(
            "playDirection inválido; se excluyen %d filas", int((~valid).sum())
        )
    out = df.loc[valid].copy()
    left = out["playDirection"].astype(str).eq("left")
    out["x_norm"] = np.where(left, FIELD_LENGTH - out["x"], out["x"])
    out["y_norm"] = np.where(left, FIELD_WIDTH - out["y"], out["y"])
    return out


# --------------------------------------------------------------------------
# Rango de frames
# --------------------------------------------------------------------------
def _as_frame(value) -> int | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        return None
    return int(value)


def find_range(play_df: pd.DataFrame, csv_snap, csv_res) -> tuple[int, int, list[str]]:
    """Devuelve ``(snap, res, avisos)`` o lanza ``SinRango``.

    ``snap`` es el primer frame con evento de snap; ``res`` el primer frame
    ``>= snap`` con evento de pase. Si falta alguno se usa ``csv_snap`` /
    ``csv_res`` (Plays_Store) y se emite un aviso. Sin valor de respaldo, o
    con ``res < snap``, lanza ``SinRango``.
    """
    warnings: list[str] = []
    ev = play_df["event"].astype("object")

    snap_rows = play_df.loc[ev.isin(SNAP_EVENTS), "frameId"]
    snap = int(snap_rows.min()) if len(snap_rows) else None
    if snap is None:
        snap = _as_frame(csv_snap)
        if snap is None:
            raise SinRango("sin evento ball_snap ni snap_frameId")
        warnings.append("Falta el evento ball_snap; se usa snap_frameId de Plays_Store")

    pass_rows = play_df.loc[ev.isin(PASS_EVENTS) & (play_df["frameId"] >= snap), "frameId"]
    res = int(pass_rows.min()) if len(pass_rows) else None
    if res is None:
        res = _as_frame(csv_res)
        if res is None:
            raise SinRango("sin evento pass_forward ni res_frameId")
        warnings.append("Falta el evento pass_forward; se usa res_frameId de Plays_Store")

    if res < snap:
        raise SinRango("pass_forward anterior a ball_snap")
    for w in warnings:
        logger.warning(w)
    return snap, res, warnings


def clip_range(play_df: pd.DataFrame, snap: int, res: int) -> pd.DataFrame:
    """Frames ``snap <= frameId <= res`` ordenados por ``frameId``."""
    m = (play_df["frameId"] >= snap) & (play_df["frameId"] <= res)
    return play_df.loc[m].sort_values(["frameId", "nflId"], kind="stable").reset_index(drop=True)


# --------------------------------------------------------------------------
# Roles y etiquetas
# --------------------------------------------------------------------------
def make_label(role: str, position) -> str:
    """Player_Label según los criterios 17.13 a 17.17."""
    pos = None
    if position is not None and not (isinstance(position, float) and np.isnan(position)):
        if not (position is pd.NA) and str(position) != "":
            pos = str(position)
    if role == "QB":
        return "QB"
    if role == "LB":
        return "LB"
    if role == "Pass Rush":
        return "Rush"
    if role == "Pass Route":
        return pos or "WR"
    if role == "Pass Block":
        return pos or "OL"
    if role == "Coverage":
        return pos or "DB"
    return pos or role


def _role_for(pff_role, official_pos) -> str | None:
    if pff_role == "Pass":
        return "QB"
    if pff_role in ("Pass Rush", "Pass Route", "Pass Block"):
        return str(pff_role)
    if pff_role == "Coverage":
        return "LB" if official_pos in LB_POSITIONS else "Coverage"
    return None


def assign_roles(
    players_df: pd.DataFrame,
    pff_roles: pd.DataFrame,
    officials,
    offense_abbr: str,
    team_map: dict | None = None,
) -> pd.DataFrame:
    """Asigna rol, posición, etiqueta, lado e ``is_lb`` a cada jugador.

    ``players_df``: filas de tracking (sin balón) con ``nflId`` y ``team``
    (``home``/``away`` o abreviatura). ``pff_roles``: ``nflId``, ``pff_role`` y
    ``pff_positionLinedUp`` de la jugada. ``officials``: Series
    ``nflId -> officialPosition``. ``team_map``: ``{"home": abbr, "away": abbr}``
    cuando ``team`` es home/away. Devuelve una fila por jugador con exactamente
    un rol; los jugadores sin fila PFF o con rol desconocido se omiten con aviso.
    ``is_lb`` = defensor con ``officialPosition`` en ``LB_POSITIONS`` (A4).
    """
    cols = ["nflId", "role", "position", "label", "side", "is_lb"]
    p = players_df[players_df["nflId"].notna()]
    p = p.drop_duplicates(subset="nflId")[["nflId", "team"]].copy()
    p["nflId"] = p["nflId"].astype("int64")

    pff = pff_roles.dropna(subset=["nflId"]).copy()
    pff["nflId"] = pff["nflId"].astype("int64")
    pff = pff.drop_duplicates(subset="nflId", keep="first").set_index("nflId")

    tm = team_map or {}
    rows = []
    for nfl_id, team in p.itertuples(index=False):
        abbr = tm.get(team, team)
        if nfl_id not in pff.index:
            logger.warning("Jugador %s sin fila PFF; se omite", nfl_id)
            continue
        row = pff.loc[nfl_id]
        official = officials.get(nfl_id) if officials is not None else None
        role = _role_for(row.get("pff_role"), official)
        if role is None:
            logger.warning("Jugador %s con pff_role %r desconocido; se omite", nfl_id, row.get("pff_role"))
            continue
        position = row.get("pff_positionLinedUp")
        position = None if (position is None or pd.isna(position)) else str(position)
        is_def = abbr != offense_abbr
        rows.append({
            "nflId": int(nfl_id),
            "role": role,
            "position": position,
            "label": make_label(role, position),
            "side": "defense" if is_def else "offense",
            "is_lb": bool(is_def and official in LB_POSITIONS),
        })
    return pd.DataFrame(rows, columns=cols)


# Carga perezosa, una sola vez y bajo lock, de las tablas de roles.
_lock = threading.Lock()
_cache: dict = {}


def load_role_tables(data_dir, keys: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.Series]:
    """Devuelve ``(pff, officials)``; se leen la primera vez y se reutilizan.

    ``pff``: gameId, playId, nflId, pff_role, pff_positionLinedUp (filtrado a
    ``keys`` con gameId/playId si se da). ``officials``: Series nflId ->
    officialPosition.
    """
    with _lock:
        if "tables" not in _cache:
            data_dir = Path(data_dir)
            pff = pd.read_csv(
                data_dir / "pffScoutingData.csv",
                usecols=["gameId", "playId", "nflId", "pff_role", "pff_positionLinedUp"],
            )
            if keys is not None:
                pff = pff.merge(
                    keys[["gameId", "playId"]].drop_duplicates(),
                    on=["gameId", "playId"],
                )
            pl = pd.read_csv(data_dir / "players.csv", usecols=["nflId", "officialPosition"])
            officials = pl.drop_duplicates("nflId").set_index("nflId")["officialPosition"]
            _cache["tables"] = (pff, officials)
        return _cache["tables"]


def reset_role_cache() -> None:
    with _lock:
        _cache.clear()
