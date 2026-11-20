"""Exploración de datos con bajo uso de memoria.

Reglas: nunca se carga un CSV completo. Solo encabezados, tamaño en disco,
conteo aproximado de filas (bytes totales / bytes promedio por fila de la
muestra) y las primeras 10,000 filas de cada tabla. Para tracking, se leen las
primeras 10,000 filas de CADA archivo (122) solo con las columnas necesarias
y se agregan contadores, nunca se concatena todo.

Uso: .venv/bin/python src/explore.py
Salida: stdout y src/explore_output.json (consumido para DATA_CONTEXT.md).
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "nfl-big-data-bowl-regional-event-data" / "data"
TRACK = DATA / "tracking"
N = 10_000
OUT = Path(__file__).resolve().parent / "explore_output.json"


def mb(path: Path) -> float:
    return round(path.stat().st_size / 1024 / 1024, 3)


def describe(path: Path) -> tuple[dict, pd.DataFrame]:
    sample = pd.read_csv(path, nrows=N, low_memory=False)
    # bytes promedio por fila a partir de la muestra (lectura binaria acotada)
    with open(path, "rb") as fh:
        header = fh.readline()
        chunk = fh.read(min(path.stat().st_size, 8 * 1024 * 1024))
    lines = max(chunk.count(b"\n"), 1)
    avg = len(chunk) / lines
    est_rows = int((path.stat().st_size - len(header)) / avg)
    info = {
        "file": path.name,
        "size_mb": mb(path),
        "est_rows": est_rows,
        "sample_rows": len(sample),
        "columns": {c: str(t) for c, t in sample.dtypes.items()},
        "null_pct_sample": {c: round(float(v), 1) for c, v in (sample.isna().mean() * 100).items()},
    }
    return info, sample


def uniques(s: pd.Series, top: int = 40) -> dict:
    vc = s.value_counts(dropna=False)
    return {"n_unique": int(s.nunique(dropna=True)),
            "values": {str(k): int(v) for k, v in vc.head(top).items()}}


def main() -> None:
    rep: dict = {"tables": {}, "uniques": {}, "horizon": {}, "keys": {}}

    # ---- tablas pequeñas / medianas
    tables = {}
    for name in ["games", "plays", "players", "pffScoutingData"]:
        info, sample = describe(DATA / f"{name}.csv")
        rep["tables"][name] = info
        tables[name] = sample
        print(f"{name}: {info['size_mb']} MB, ~{info['est_rows']} filas, {len(info['columns'])} cols")

    # ---- tracking: encabezados de TODOS los archivos, muestra por archivo
    files = sorted(TRACK.glob("tracking_*.csv"))
    headers = {}
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            headers[f.name] = fh.readline().strip()
    rep["tracking_header_consistent"] = len(set(headers.values())) == 1
    first_info, first_sample = describe(files[0])
    total_mb = round(sum(f.stat().st_size for f in files) / 1024 / 1024, 2)
    est_total = 0
    ev_counter: Counter = Counter()
    team_counter: Counter = Counter()
    dir_counter: Counter = Counter()
    games_in_tracking, plays_per_file = set(), []
    maxima = {"s": 0.0, "a": 0.0}
    frames_max = 0
    for f in files:
        with open(f, "rb") as fh:
            hdr = fh.readline()
            chunk = fh.read(2 * 1024 * 1024)
        avg = len(chunk) / max(chunk.count(b"\n"), 1)
        est_total += int((f.stat().st_size - len(hdr)) / avg)
        s = pd.read_csv(f, nrows=N, usecols=["gameId", "playId", "frameId", "event", "team",
                                             "playDirection", "s", "a"], low_memory=False)
        ev_counter.update(s["event"].fillna("<NA>").value_counts().to_dict())
        team_counter.update({"football" if t == "football" else "player": c
                             for t, c in s["team"].value_counts().items()})
        dir_counter.update(s["playDirection"].value_counts().to_dict())
        games_in_tracking.update(s["gameId"].unique().tolist())
        maxima["s"] = max(maxima["s"], float(s["s"].max()))
        maxima["a"] = max(maxima["a"], float(s["a"].max()))
        frames_max = max(frames_max, int(s["frameId"].max()))
    rep["tables"]["tracking (122 archivos)"] = {
        "file": "tracking/tracking_[gameId].csv",
        "n_files": len(files),
        "size_mb": total_mb,
        "est_rows": est_total,
        "sample_rows": f"{N} por archivo",
        "columns": first_info["columns"],
        "null_pct_sample": first_info["null_pct_sample"],
    }
    print(f"tracking: {len(files)} archivos, {total_mb} MB, ~{est_total} filas estimadas")
    rep["uniques"]["tracking.event (muestra 10k filas/archivo)"] = {
        "n_unique": len(ev_counter), "values": dict(ev_counter.most_common(60))}
    # Verificación del vocabulario completo de eventos: solo la columna `event`,
    # en chunks de 200k filas (memoria acotada), para no depender de la muestra.
    ev_full: Counter = Counter()
    for f in files:
        for ch in pd.read_csv(f, usecols=["event"], chunksize=200_000):
            ev_full.update(ch["event"].dropna().value_counts().to_dict())
    rep["uniques"]["tracking.event (escaneo completo por chunks, filas con evento)"] = {
        "n_unique": len(ev_full), "values": dict(ev_full.most_common())}
    rep["uniques"]["tracking.playDirection"] = dict(dir_counter)
    rep["uniques"]["tracking.team (jugador vs balón, muestra)"] = dict(team_counter)
    rep["tracking_sample_stats"] = {"max_speed_yds_s": round(maxima["s"], 2),
                                    "max_accel": round(maxima["a"], 2),
                                    "max_frameId_en_muestra": frames_max,
                                    "gameIds_en_muestra": len(games_in_tracking)}

    # ---- horizonte temporal (games.csv es pequeño; muestra = tabla completa si <10k)
    g = tables["games"]
    rep["horizon"] = {
        "seasons": sorted(g["season"].unique().tolist()),
        "weeks": sorted(g["week"].unique().tolist()),
        "n_games": int(g["gameId"].nunique()),
        "date_min": str(g["gameDate"].min()), "date_max": str(g["gameDate"].max()),
        "games_with_tracking_file": len(files),
        "tracking_ids_match_games": sorted(int(f.stem.split("_")[1]) for f in files)
        == sorted(g["gameId"].tolist()),
        "teams": int(pd.concat([g["homeTeamAbbr"], g["visitorTeamAbbr"]]).nunique()),
    }

    # ---- valores únicos de columnas clave (muestra 10k filas)
    p, pf, pl = tables["plays"], tables["pffScoutingData"], tables["players"]
    for col in ["down", "quarter", "offenseFormation", "personnelO", "personnelD", "defendersInBox",
                "dropBackType", "pff_playAction", "pff_passCoverage", "pff_passCoverageType",
                "passResult", "yardsToGo"]:
        if col in p:
            rep["uniques"][f"plays.{col}"] = uniques(p[col], 25 if col != "yardsToGo" else 10)
    for col in ["pff_role", "pff_positionLinedUp", "pff_blockType", "pff_hit", "pff_hurry",
                "pff_sack", "pff_beatenByDefender"]:
        rep["uniques"][f"pffScoutingData.{col}"] = uniques(pf[col], 30)
    rep["uniques"]["players.officialPosition"] = uniques(pl["officialPosition"], 30)
    rep["uniques"]["players.collegeName"] = {"n_unique": int(pl["collegeName"].nunique())}
    rep["uniques"]["plays.playResult (describe)"] = {
        k: round(float(v), 2) for k, v in p["playResult"].describe().items()}

    # ---- llaves de unión: validación de cobertura en la muestra
    keys = {
        "games.gameId <-> plays.gameId": "gameId",
        "plays(gameId,playId) <-> pffScoutingData(gameId,playId)": "gameId+playId",
        "pffScoutingData.nflId <-> players.nflId": "nflId",
        "tracking(gameId,playId,nflId,frameId)": "gameId+playId+nflId+frameId",
    }
    rep["keys"] = keys
    rep["key_checks"] = {
        "plays.gameId en games": float(p["gameId"].isin(g["gameId"]).mean()),
        "pff.nflId en players (muestra)": float(pf["nflId"].isin(pl["nflId"]).mean()),
        "pff (gameId,playId) en plays (muestra)": float(
            pf.merge(p[["gameId", "playId"]], on=["gameId", "playId"], how="left", indicator=True)
            ["_merge"].eq("both").mean()),
        "plays.(gameId,playId) duplicados (muestra)": int(p.duplicated(["gameId", "playId"]).sum()),
        "games con jugadas en la muestra de plays": int(p["gameId"].nunique()),
    }

    # ---- columnas de métricas físicas / biométricas disponibles
    rep["players_extra"] = {
        "height_ejemplos": pl["height"].dropna().head(5).tolist(),
        "birthDate_nulos_pct": round(float(pl["birthDate"].isna().mean() * 100), 1),
        "weight_describe": {k: round(float(v), 1) for k, v in pl["weight"].describe().items()},
        "n_players_tabla": len(pl),
    }

    # plays.csv (2 MB, 8.5k filas) cabe en la muestra completa: señal rápida de coberturas
    rep["plays_signal"] = {
        "playResult_medio_por_cobertura": {k: round(float(v), 2) for k, v in
                                            p.groupby("pff_passCoverage")["playResult"].mean().items()},
        "playResult_medio_play_action": {str(k): round(float(v), 2) for k, v in
                                          p.groupby("pff_playAction")["playResult"].mean().items()},
        "passResult_nulos": int(p["passResult"].isna().sum()),
    }

    OUT.write_text(json.dumps(rep, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps(rep, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
