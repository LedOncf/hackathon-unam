"""Métricas de tracking por jugada para el perfil Coach.

Este módulo no ejecuta código al importarse. Las funciones de esta sección
(constantes, contexto y funciones base) son puras sobre DataFrames.
"""
from __future__ import annotations

import gc
import logging
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src.features import RunReport

logger = logging.getLogger(__name__)

KEYS = ["gameId", "playId"]

TRACKING_COLUMNS = [
    "gameId", "playId", "nflId", "frameId", "time", "team",
    "playDirection", "x", "y", "s", "a", "event",
]
# `time` se lee como str (se parsea en add_time_seconds).
TRACKING_DTYPES = {
    "gameId": "int32", "playId": "int32", "nflId": "float64",
    "frameId": "int16", "team": "category", "playDirection": "category",
    "event": "category", "x": "float64", "y": "float64",
    "s": "float32", "a": "float32",
}
SNAP_EVENTS = {"ball_snap", "autoevent_ballsnap"}
RESOLUTION_EVENTS = {"pass_forward", "autoevent_passforward", "qb_sack", "qb_strip_sack"}
LB_POSITIONS = {"ILB", "MLB", "OLB", "LB"}
SPEED_MAX = 15.0
BITE_OFFSET_FRAMES = 10
FRAME_RATE_HZ = 10.0  # frameId avanza a 10 Hz (0.1 s por frame)

FIELD_LENGTH = 120.0
FIELD_WIDTH = 53.3


@dataclass
class TrackingContext:
    pff_roles: pd.DataFrame      # gameId, playId, nflId, pff_role, officialPosition
    plays_def: pd.DataFrame      # gameId, playId, defensiveTeam
    positions: pd.Series         # index nflId -> officialPosition
    team_map: dict[int, dict]    # gameId -> {"home": abbr, "away": abbr}


def build_context(tables: dict, features: pd.DataFrame) -> TrackingContext:
    """Construye los datos auxiliares que se reutilizan en cada archivo."""
    players = tables["players"][["nflId", "officialPosition"]].drop_duplicates(
        subset="nflId", keep="first"
    )
    positions = players.set_index("nflId")["officialPosition"]

    pff = tables["pff"][KEYS + ["nflId", "pff_role"]].copy()
    pff = pff.merge(players, on="nflId", how="left")

    plays_def = (
        features[KEYS + ["defensiveTeam"]]
        .drop_duplicates(subset=KEYS, keep="first")
        .reset_index(drop=True)
    )

    games = tables["games"]
    team_map: dict[int, dict] = {
        int(r.gameId): {"home": r.homeTeamAbbr, "away": r.visitorTeamAbbr}
        for r in games[["gameId", "homeTeamAbbr", "visitorTeamAbbr"]].itertuples(index=False)
    }
    return TrackingContext(
        pff_roles=pff.reset_index(drop=True),
        plays_def=plays_def,
        positions=positions,
        team_map=team_map,
    )


def normalize_xy(
    df: pd.DataFrame, run: RunReport | None = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Agrega ``x_norm`` y ``y_norm`` (ofensiva hacia +X).

    Excluye las filas con ``playDirection`` distinto de left/right y devuelve
    también las llaves (gameId, playId) afectadas, que se registran.
    """
    valid = df["playDirection"].isin(["left", "right"])
    bad = df.loc[~valid, KEYS].drop_duplicates().reset_index(drop=True)
    if len(bad):
        msg = "playDirection inválido en jugadas: " + ", ".join(
            f"({g},{p})" for g, p in bad.itertuples(index=False)
        )
        if run is not None:
            run.warn(msg)
        else:
            logger.warning(msg)
    out = df.loc[valid].copy()
    left = out["playDirection"].astype(str).eq("left")
    out["x_norm"] = np.where(left, FIELD_LENGTH - out["x"], out["x"])
    out["y_norm"] = np.where(left, FIELD_WIDTH - out["y"], out["y"])
    return out, bad


def filter_speed(df: pd.DataFrame, smax: float = SPEED_MAX) -> pd.DataFrame:
    """Pone NaN en ``s`` cuando ``s > smax``; conserva filas y posiciones."""
    out = df.copy()
    out["s"] = out["s"].where(~(out["s"] > smax))
    return out


def add_time_seconds(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte ``time`` (str) a ``time_s`` (float64, segundos relativos).

    Factoriza ``time`` y parsea solo los valores únicos. El origen es el
    menor tiempo del DataFrame; valores no parseables quedan en NaN.
    """
    out = df.copy()
    codes, uniques = pd.factorize(out["time"].astype("object"))
    parsed = pd.to_datetime(pd.Series(uniques), errors="coerce")
    if len(parsed) and parsed.notna().any():
        secs = (parsed - parsed.min()).dt.total_seconds().to_numpy(dtype="float64")
    else:
        secs = np.full(len(parsed), np.nan)
    lookup = np.append(secs, np.nan)  # código -1 (nulo) -> último elemento
    out["time_s"] = lookup[codes]
    return out


def _frame_table(df: pd.DataFrame) -> pd.DataFrame:
    """Un registro por frame (los eventos se repiten en todas las filas)."""
    cols = KEYS + ["frameId", "time_s", "event"]
    return df[cols].dropna(subset=["time_s"]).drop_duplicates(KEYS + ["frameId", "event"])


def find_event_frames(df: pd.DataFrame) -> pd.DataFrame:
    """Frame_Snap, Frame_Resolucion y ``time_to_throw`` por jugada.

    Requiere ``time_s`` (ver ``add_time_seconds``). Devuelve una fila por
    jugada con snap o resolución: gameId, playId, snap_frameId, snap_time,
    res_frameId, res_time, time_to_throw. La resolución es el primer evento
    con ``time >=`` snap (D3); ``time_to_throw = (res_frameId - snap_frameId)
    / 10`` (frames a 10 Hz), nulo si falta snap o resolución o si resultara
    negativo.
    """
    fr = _frame_table(df)
    ev = fr["event"].astype("object")

    snap = (
        fr[ev.isin(SNAP_EVENTS)]
        .sort_values(KEYS + ["time_s", "frameId"])
        .groupby(KEYS, as_index=False)
        .first()
        .rename(columns={"frameId": "snap_frameId", "time_s": "snap_time"})
        [KEYS + ["snap_frameId", "snap_time"]]
    )

    res = fr.loc[ev.isin(RESOLUTION_EVENTS), KEYS + ["frameId", "time_s"]]
    res = res.merge(snap[KEYS + ["snap_time"]], on=KEYS, how="left")
    res = res[res["snap_time"].isna() | (res["time_s"] >= res["snap_time"])]
    res = (
        res.sort_values(KEYS + ["time_s", "frameId"])
        .groupby(KEYS, as_index=False)
        .first()
        .rename(columns={"frameId": "res_frameId", "time_s": "res_time"})
        [KEYS + ["res_frameId", "res_time"]]
    )

    out = snap.merge(res, on=KEYS, how="outer")
    for c in ("snap_frameId", "res_frameId"):
        out[c] = out[c].astype("Int16")
    # `time` solo tiene resolución de 1 s; los frames avanzan a 10 Hz, así que
    # el tiempo se calcula con frameId (0.1 s por frame).
    ttt = ((out["res_frameId"].astype("float64") - out["snap_frameId"].astype("float64"))
           / FRAME_RATE_HZ).round(2)
    out["time_to_throw"] = ttt.where(ttt >= 0)
    return out.sort_values(KEYS).reset_index(drop=True)


def frame_dt_flags(df: pd.DataFrame) -> pd.DataFrame:
    """``n_frames``, ``frame_dt_ok`` y ``mean_dt_time`` por jugada.

    ``frame_dt_ok`` = 1 si hay >= 2 frames, los ``frameId`` consecutivos
    (ordenados) avanzan siempre de 1 en 1 y ``time_s`` es monótono no
    decreciente al ordenar por ``frameId``. ``mean_dt_time`` es el dt medio
    por ``time`` ``(max - min)/(n - 1)``, solo diagnóstico (resolución 1 s).
    """
    fr = (
        df[KEYS + ["frameId", "time_s"]]
        .dropna(subset=["time_s"])
        .drop_duplicates(KEYS + ["frameId"])
        .sort_values(KEYS + ["frameId"])
    )
    g = fr.groupby(KEYS, sort=True)
    d_fid = g["frameId"].diff()
    d_t = g["time_s"].diff()
    bad = pd.DataFrame({
        "gameId": fr["gameId"], "playId": fr["playId"],
        "gap": d_fid.notna() & (d_fid != 1),
        "back": d_t.notna() & (d_t < 0),
    }).groupby(KEYS)[["gap", "back"]].any()
    t = g["time_s"].agg(["min", "max", "size"])
    n = t["size"].to_numpy()
    denom = np.where(n >= 2, n - 1, 1)
    mean_dt = (t["max"] - t["min"]).to_numpy() / denom
    ok = (n >= 2) & ~bad["gap"].to_numpy() & ~bad["back"].to_numpy()
    out = t.reset_index()[KEYS].copy()
    out["n_frames"] = n.astype("int16")
    out["frame_dt_ok"] = ok.astype("int8")
    out["mean_dt_time"] = np.where(n >= 2, mean_dt, np.nan).astype("float32")
    return out


def select_passer(
    df: pd.DataFrame,
    roles: pd.DataFrame,
    positions: pd.Series,
    run: RunReport | None = None,
) -> pd.DataFrame:
    """Elige el Pasador de cada jugada.

    Fuente principal: ``pff_role == "Pass"`` (menor ``nflId`` en empate).
    Respaldo, solo si la jugada no tiene ningún ``Pass``: jugador con
    ``officialPosition == "QB"`` presente en el tracking (``df``) o en
    ``roles`` de la jugada. Devuelve gameId, playId, passer_nflId (Int64),
    passer_source ("pff" | "qb_fallback") y passer_ambiguous (bool); solo
    incluye jugadas con Pasador. Las ambigüedades se registran con la llave.
    """
    primary = (
        roles.loc[roles["pff_role"].eq("Pass"), KEYS + ["nflId"]]
        .dropna()
        .groupby(KEYS)["nflId"]
        .agg(passer_nflId="min", n="nunique")
        .reset_index()
    )
    primary["passer_source"] = "pff"

    ids = pd.concat(
        [df[KEYS + ["nflId"]], roles[KEYS + ["nflId"]]], ignore_index=True
    ).dropna().drop_duplicates()
    pos = ids["nflId"].map(positions)
    qb = (
        ids[pos.eq("QB")]
        .merge(primary[KEYS], on=KEYS, how="left", indicator=True)
        .query("_merge == 'left_only'")
        .groupby(KEYS)["nflId"]
        .agg(passer_nflId="min", n="nunique")
        .reset_index()
    )
    qb["passer_source"] = "qb_fallback"

    out = pd.concat([primary, qb], ignore_index=True)
    if out.empty:
        return pd.DataFrame({
            "gameId": pd.Series(dtype="int32"),
            "playId": pd.Series(dtype="int32"),
            "passer_nflId": pd.Series(dtype="Int64"),
            "passer_source": pd.Series(dtype="string"),
            "passer_ambiguous": pd.Series(dtype="bool"),
        })
    out["passer_ambiguous"] = out["n"] > 1
    amb = out[out["passer_ambiguous"]]
    if len(amb):
        msg = "Pasador ambiguo (se usa el menor nflId) en jugadas: " + ", ".join(
            f"({g},{p})" for g, p in amb[KEYS].itertuples(index=False)
        )
        if run is not None:
            run.warn(msg)
        else:
            logger.warning(msg)
    out["passer_nflId"] = out["passer_nflId"].astype("Int64")
    out["passer_source"] = out["passer_source"].astype("string")
    return (
        out[KEYS + ["passer_nflId", "passer_source", "passer_ambiguous"]]
        .sort_values(KEYS)
        .reset_index(drop=True)
    )


def rusher_distance(
    df: pd.DataFrame,
    frames: pd.DataFrame,
    roles: pd.DataFrame,
    passer: pd.DataFrame,
) -> pd.DataFrame:
    """``min_rusher_dist_at_throw`` por jugada (yardas, 2 decimales).

    Distancia euclidiana mínima, en el Frame_Resolucion, entre el Pasador y
    los jugadores ``Pass Rush`` con ``x_norm``/``y_norm``. Devuelve una fila
    por jugada de ``frames``; el valor es nulo si no hay Resolución, Pasador,
    rusher o coordenadas.
    """
    out = frames[KEYS].drop_duplicates().reset_index(drop=True)

    at_res = df.merge(
        frames[KEYS + ["res_frameId"]].dropna(subset=["res_frameId"]).astype(
            {"res_frameId": "int64"}
        ),
        left_on=KEYS + ["frameId"],
        right_on=KEYS + ["res_frameId"],
    )[KEYS + ["nflId", "x_norm", "y_norm"]]
    at_res = at_res.dropna(subset=["nflId", "x_norm", "y_norm"]).drop_duplicates(
        KEYS + ["nflId"]
    )

    rush_ids = roles.loc[roles["pff_role"].eq("Pass Rush"), KEYS + ["nflId"]].drop_duplicates()
    rush = at_res.merge(rush_ids, on=KEYS + ["nflId"])
    pas = passer[KEYS + ["passer_nflId"]].dropna().astype({"passer_nflId": "float64"})
    pas = at_res.merge(pas, left_on=KEYS + ["nflId"], right_on=KEYS + ["passer_nflId"])[
        KEYS + ["x_norm", "y_norm"]
    ]
    d = rush.merge(pas, on=KEYS, suffixes=("_r", "_p"))
    d["dist"] = np.hypot(d["x_norm_r"] - d["x_norm_p"], d["y_norm_r"] - d["y_norm_p"])
    dist = d.groupby(KEYS, as_index=False)["dist"].min()
    dist["min_rusher_dist_at_throw"] = dist["dist"].round(2)

    return out.merge(dist[KEYS + ["min_rusher_dist_at_throw"]], on=KEYS, how="left")


def normalize_team(df: pd.DataFrame, team_map: dict[int, dict]) -> pd.DataFrame:
    """Agrega ``team_abbr``: abreviatura de equipo (D8).

    Si ``team`` es ``home``/``away`` se mapea con ``team_map`` (por gameId);
    si ya es una abreviatura se usa tal cual. ``football`` se conserva.
    """
    out = df.copy()
    team = out["team"].astype("object")
    home = out["gameId"].map({g: m["home"] for g, m in team_map.items()})
    away = out["gameId"].map({g: m["away"] for g, m in team_map.items()})
    abbr = team.where(~team.eq("home"), home)
    abbr = abbr.where(~team.eq("away"), away)
    out["team_abbr"] = abbr
    return out


def lb_bite(
    df: pd.DataFrame,
    frames: pd.DataFrame,
    positions: pd.Series,
    plays_def: pd.DataFrame,
    team_map: dict[int, dict] | None = None,
) -> pd.DataFrame:
    """``lb_bite_yards`` y ``n_lb_used`` por jugada.

    Promedio, sobre los Linebackers de la defensa (``officialPosition`` en
    ``LB_POSITIONS``), de ``x_norm`` en el Frame_Snap menos ``x_norm`` en el
    frame ``snap_frameId + BITE_OFFSET_FRAMES``, usando solo los que tienen
    ambos valores; redondeado a 2 decimales. Positivo = avanzó hacia la línea
    de golpeo. Nulo si no existe el frame snap+10 o no hay valores. Devuelve
    una fila por jugada de ``frames`` con snap.
    """
    snaps = frames[KEYS + ["snap_frameId"]].dropna(subset=["snap_frameId"])
    snaps = snaps.astype({"snap_frameId": "int64"}).drop_duplicates(KEYS)
    out = snaps[KEYS].reset_index(drop=True)

    d = df if "team_abbr" in df.columns else normalize_team(df, team_map or {})
    lb_ids = positions.index[positions.isin(LB_POSITIONS)]
    d = d[d["nflId"].isin(lb_ids)]
    d = d.merge(plays_def[KEYS + ["defensiveTeam"]], on=KEYS)
    d = d[d["team_abbr"].eq(d["defensiveTeam"])]
    d = d[KEYS + ["nflId", "frameId", "x_norm"]].dropna(subset=["nflId", "x_norm"])
    d = d.astype({"frameId": "int64"}).drop_duplicates(KEYS + ["nflId", "frameId"])

    a = d.merge(snaps, left_on=KEYS + ["frameId"], right_on=KEYS + ["snap_frameId"])
    b = d.assign(snap_frameId=d["frameId"] - BITE_OFFSET_FRAMES).merge(
        snaps, on=KEYS + ["snap_frameId"]
    )
    m = a[KEYS + ["nflId", "x_norm"]].merge(
        b[KEYS + ["nflId", "x_norm"]], on=KEYS + ["nflId"], suffixes=("_0", "_10")
    )
    m["bite"] = m["x_norm_0"] - m["x_norm_10"]
    lb = m.groupby(KEYS, as_index=False).agg(
        lb_bite_yards=("bite", "mean"), n_lb_used=("bite", "size")
    )
    lb["lb_bite_yards"] = lb["lb_bite_yards"].round(2)
    out = out.merge(lb, on=KEYS, how="left")
    out["n_lb_used"] = out["n_lb_used"].astype("Int8")
    return out


AGG_COLUMNS = [
    "gameId", "playId", "n_frames", "snap_frameId", "res_frameId",
    "time_to_throw", "frame_dt_ok", "mean_dt_time", "passer_nflId", "passer_source",
    "passer_ambiguous", "min_rusher_dist_at_throw", "n_lb_used",
    "lb_bite_yards", "n_speed_outliers", "max_speed_player",
]


def _empty_aggregate() -> pd.DataFrame:
    dtypes = {
        "gameId": "int32", "playId": "int32", "n_frames": "int16",
        "snap_frameId": "Int16", "res_frameId": "Int16",
        "time_to_throw": "float64", "frame_dt_ok": "int8",
        "mean_dt_time": "float32", "passer_nflId": "Int64", "passer_source": "string",
        "passer_ambiguous": "bool", "min_rusher_dist_at_throw": "float64",
        "n_lb_used": "Int8", "lb_bite_yards": "float64",
        "n_speed_outliers": "int16", "max_speed_player": "float32",
    }
    return pd.DataFrame({c: pd.Series(dtype=t) for c, t in dtypes.items()})[AGG_COLUMNS]


def process_tracking_frame(
    df: pd.DataFrame, ctx: TrackingContext, run: RunReport | None = None
) -> pd.DataFrame:
    """Núcleo sin I/O: una fila por jugada con todas las columnas del agregado.

    ``df`` contiene las filas de tracking (con ``time`` como str) de uno o más
    juegos. El balón (``team == "football"``) se excluye de las métricas de
    jugadores; los frames y eventos se toman de todas las filas.
    """
    if df.empty:
        return _empty_aggregate()

    d, _bad = normalize_xy(df, run)
    if d.empty:
        return _empty_aggregate()
    d = add_time_seconds(d)
    d = normalize_team(d, ctx.team_map)

    football = d["team"].astype("object").eq("football")
    players = d.loc[~football]

    # Diagnóstico de velocidad (D10): s > 15 se descarta antes de agregar.
    n_out = (
        players.assign(_o=players["s"] > SPEED_MAX)
        .groupby(KEYS)["_o"].sum().astype("int16").rename("n_speed_outliers")
        .reset_index()
    )
    players = filter_speed(players)
    max_s = players.groupby(KEYS)["s"].max().rename("max_speed_player").reset_index()

    dt = frame_dt_flags(d)
    frames = find_event_frames(d)

    game_ids = d["gameId"].unique()
    roles = ctx.pff_roles[ctx.pff_roles["gameId"].isin(game_ids)]
    plays_def = ctx.plays_def[ctx.plays_def["gameId"].isin(game_ids)]

    passer = select_passer(players, roles, ctx.positions, run)
    rusher = rusher_distance(players, frames, roles, passer)
    bite = lb_bite(players, frames, ctx.positions, plays_def, ctx.team_map)

    out = dt.merge(
        frames[KEYS + ["snap_frameId", "res_frameId", "time_to_throw"]],
        on=KEYS, how="left",
    )
    out = out.merge(passer, on=KEYS, how="left")
    out = out.merge(rusher, on=KEYS, how="left")
    out = out.merge(bite[KEYS + ["n_lb_used", "lb_bite_yards"]], on=KEYS, how="left")
    out = out.merge(n_out, on=KEYS, how="left").merge(max_s, on=KEYS, how="left")

    out["n_speed_outliers"] = out["n_speed_outliers"].fillna(0).astype("int16")
    out["max_speed_player"] = out["max_speed_player"].astype("float32")
    out["passer_ambiguous"] = out["passer_ambiguous"].fillna(False).astype(bool)
    out["gameId"] = out["gameId"].astype("int32")
    out["playId"] = out["playId"].astype("int32")
    for c in ("snap_frameId", "res_frameId"):
        out[c] = out[c].astype("Int16")
    out["n_lb_used"] = out["n_lb_used"].astype("Int8")
    out["passer_nflId"] = out["passer_nflId"].astype("Int64")
    out["passer_source"] = out["passer_source"].astype("string")
    return out[AGG_COLUMNS].sort_values(KEYS).reset_index(drop=True)


def process_tracking_file(
    path, ctx: TrackingContext, run: RunReport | None = None
) -> pd.DataFrame:
    """Lee un archivo de tracking (solo columnas requeridas) y lo agrega."""
    df = pd.read_csv(
        path, usecols=TRACKING_COLUMNS,
        dtype={**TRACKING_DTYPES, "time": "str"},
    )
    try:
        return process_tracking_frame(df, ctx, run)
    finally:
        del df


def compute_tracking_metrics(
    tracking_dir,
    ctx: TrackingContext,
    run: RunReport | None = None,
    game_ids=None,
) -> tuple[pd.DataFrame, dict]:
    """Procesa los archivos de tracking uno a la vez.

    Devuelve (agregado, {"ok", "error", "attempted"}). Los archivos con error
    se registran y se omiten sin conservar métricas parciales.
    """
    tracking_dir = Path(tracking_dir)
    if game_ids is None:
        paths = sorted(tracking_dir.glob("tracking_*.csv"))
    else:
        paths = [tracking_dir / f"tracking_{int(g)}.csv" for g in sorted(game_ids)]

    parts: list[pd.DataFrame] = []
    ok = error = 0
    for path in paths:
        t0 = time.perf_counter()
        try:
            agg = process_tracking_file(path, ctx, run)
        except (OSError, ValueError, KeyError, pd.errors.ParserError) as exc:
            error += 1
            game = path.stem.replace("tracking_", "")
            msg = f"Tracking omitido gameId={game}: {type(exc).__name__}: {exc}"
            if run is not None:
                run.warn(msg)
                run.add("tracking_error")
            else:
                logger.warning(msg)
            continue
        parts.append(agg)
        ok += 1
        if run is not None:
            run.add("tracking_ok")
        logger.info("%s: %d jugadas en %.2f s", path.name, len(agg), time.perf_counter() - t0)
        del agg
        gc.collect()

    result = pd.concat(parts, ignore_index=True) if parts else _empty_aggregate()
    counts = {"ok": ok, "error": error, "attempted": len(paths)}
    return result, counts
