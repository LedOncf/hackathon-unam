"""Genera una muestra ligera de tracking para la pizarra del dashboard publicado.

La plataforma no despliega `data/` (810 MB). Este script recorta jugadas reales
(frames snap..pass_forward) a `backend/assets/tracking_sample/`, que sí viaja
con `backend/`. Procesa un archivo de tracking a la vez.

Uso: .venv/bin/python -m src.build_tracking_sample [N_JUGADAS]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "nfl-big-data-bowl-regional-event-data" / "data"
OUT = ROOT / "backend" / "assets" / "tracking_sample"
MASTER = ROOT / "outputs" / "plays_enriched.csv"
COLS = ["gameId", "playId", "nflId", "frameId", "team", "playDirection", "x", "y", "s", "a", "event"]
SEED = 2021


def choose(master: pd.DataFrame, n_total: int) -> pd.DataFrame:
    """Muestra estratificada: cubre cada cobertura x formación y los casos
    que la pizarra prefiere (mordida alta con éxito, blitz con presión)."""
    df = master[
        master["has_tracking"].astype(bool)
        & master["snap_frameId"].notna()
        & master["res_frameId"].notna()
        & master["down"].isin([1, 2, 3, 4])
    ].copy()
    rng = np.random.default_rng(SEED)
    df["_r"] = rng.random(len(df))
    df["_pref"] = (
        ((df["pff_playAction"] == 1) & (df["is_success"] == 1) & (df["lb_bite_yards"] >= 1.16))
        | ((df["is_blitz"] == 1) & (df["any_pressure"] == 1))
    )
    df = df.sort_values(["_pref", "_r"], ascending=[False, True])
    picks = []
    for _, g in df.groupby(["pff_passCoverage", "offenseFormation"], dropna=False):
        picks.append(g.head(4))
    chosen = pd.concat(picks)
    rest = df.drop(chosen.index).sort_values("_r")
    chosen = pd.concat([chosen, rest.head(max(0, n_total - len(chosen)))])
    return chosen.head(max(n_total, len(chosen)))


def main(n_total: int = 400) -> None:
    master = pd.read_csv(MASTER)
    sel = choose(master, n_total)
    keys = set(zip(sel["gameId"].astype(int), sel["playId"].astype(int)))
    snaps = {(int(r.gameId), int(r.playId)): (int(r.snap_frameId), int(r.res_frameId))
             for r in sel.itertuples()}
    (OUT / "tracking").mkdir(parents=True, exist_ok=True)
    for f in (OUT / "tracking").glob("*.csv"):
        f.unlink()

    kept = []
    for gid in sorted({g for g, _ in keys}):
        path = DATA / "tracking" / f"tracking_{gid}.csv"
        df = pd.read_csv(path, usecols=COLS)
        plays = {p for g, p in keys if g == gid}
        df = df[df["playId"].isin(plays)]
        parts = []
        for pid, g in df.groupby("playId"):
            snap, res = snaps[(gid, int(pid))]
            parts.append(g[(g["frameId"] >= snap) & (g["frameId"] <= res)])
        if not parts:
            continue
        out = pd.concat(parts)
        for c in ("x", "y", "s", "a"):
            out[c] = out[c].round(2)
        out.to_csv(OUT / "tracking" / f"tracking_{gid}.csv", index=False)
        kept += [(gid, int(p)) for p in out["playId"].unique()]

    pff = pd.read_csv(DATA / "pffScoutingData.csv",
                      usecols=["gameId", "playId", "nflId", "pff_role", "pff_positionLinedUp"])
    pff = pff[[(g, p) in set(kept) for g, p in zip(pff["gameId"], pff["playId"])]]
    pff.to_csv(OUT / "pffScoutingData.csv", index=False)
    pd.read_csv(DATA / "players.csv", usecols=["nflId", "officialPosition"]).to_csv(
        OUT / "players.csv", index=False)
    pd.DataFrame({"play_id": [f"{g}-{p}" for g, p in sorted(kept)]}).to_csv(
        OUT / "manifest.csv", index=False)
    size = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file()) / 1e6
    print(f"{len(kept)} jugadas en {len({g for g, _ in kept})} juegos, {size:.1f} MB en {OUT}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 400)
