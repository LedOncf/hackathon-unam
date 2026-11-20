"""Verificación de supuestos del diseño con los datos reales.

Escribe ``outputs/VERIFICATION_RUN.md``. Uso: ``.venv/bin/python -m src.verify_data``.

Revisa (un archivo de tracking a la vez):
  1. Formato crudo de ``time`` en los 122 archivos (resolución, fracciones,
     frames por marca de tiempo, monotonía).
  2. Valores de ``team`` (home/away o abreviaturas) en una muestra.
  3. Coincidencia del rol PFF ``Pass`` con ``officialPosition == "QB"``.
  4. ``frame_dt_ok`` y distribución del dt promedio, y comparación de
     ``time_to_throw`` basado en ``frameId`` y ``mean_dt_time``.
  5. Tiempo por archivo y memoria máxima (``resource``).

Este módulo no ejecuta código al importarse.
"""
from __future__ import annotations

import gc
import logging
import os
import resource
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from src.features import (
    OUTPUT_DIR, TRACKING_DIR, PipelineError, RunReport, build_features,
    load_base_tables,
)
from src.tracking_metrics import (
    KEYS, TRACKING_COLUMNS, TRACKING_DTYPES, build_context,
    process_tracking_frame,
)

logger = logging.getLogger(__name__)

SAMPLE_SIZE = 10
RE_NO_FRAC = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
RE_FRAC = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z?$"


def _maxrss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0  # KB -> MB (Linux)


def _read_full(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, usecols=TRACKING_COLUMNS, dtype={**TRACKING_DTYPES, "time": "str"})


def scan_time_file(path: Path) -> dict:
    """Diagnóstico del formato crudo de ``time`` en un archivo."""
    df = pd.read_csv(
        path, usecols=["gameId", "playId", "frameId", "time"],
        dtype={"gameId": "int32", "playId": "int32", "frameId": "int16", "time": "str"},
    )
    n_rows = len(df)
    uniq = pd.Series(df["time"].dropna().unique())
    n_no_frac = int(uniq.str.match(RE_NO_FRAC).sum())
    n_frac = int(uniq.str.match(RE_FRAC).sum())
    parsed = pd.to_datetime(uniq, errors="coerce", utc=True, format="ISO8601")
    n_unparsed = int(parsed.isna().sum())
    examples = uniq.head(3).tolist()

    # Una fila por frame, ordenada por frameId dentro de la jugada.
    fr = (df.drop_duplicates(KEYS + ["frameId"]).sort_values(KEYS + ["frameId"])
          .reset_index(drop=True))
    tmap = dict(zip(uniq, parsed.astype("int64") / 1e9))
    fr["t"] = fr["time"].map(tmap)
    same_play = (fr["playId"].eq(fr["playId"].shift()) & fr["gameId"].eq(fr["gameId"].shift()))
    dt = (fr["t"] - fr["t"].shift()).where(same_play)
    dframe = (fr["frameId"].astype("int32") - fr["frameId"].shift().astype("float64")).where(same_play)

    # Frames por marca de tiempo distinta dentro de cada jugada.
    per_ts = fr.groupby(KEYS + ["t"]).size()
    out = {
        "rows": n_rows,
        "frames": len(fr),
        "plays": int(fr[KEYS].drop_duplicates().shape[0]),
        "uniq_time": len(uniq),
        "uniq_no_frac": n_no_frac,
        "uniq_frac": n_frac,
        "unparsed": n_unparsed,
        "examples": examples,
        "pairs": int(dt.notna().sum()),
        "pairs_dt0": int((dt == 0).sum()),
        "pairs_dt_neg": int((dt < 0).sum()),
        "dt_counter": Counter(dt.dropna().round(3).tolist()),
        "frameid_gap_counter": Counter(dframe.dropna().astype(int).tolist()),
        "frames_per_ts": Counter(per_ts.tolist()),
        "integer_secs": int(((fr["t"] % 1) == 0).sum()),
    }
    del df, fr, per_ts, dt, dframe
    return out


def scan_all_time(paths: list[Path]) -> dict:
    agg: dict = {
        "files": 0, "rows": 0, "frames": 0, "plays": 0, "uniq_time": 0,
        "uniq_no_frac": 0, "uniq_frac": 0, "unparsed": 0, "pairs": 0,
        "pairs_dt0": 0, "pairs_dt_neg": 0, "integer_secs": 0,
        "dt_counter": Counter(), "frameid_gap_counter": Counter(),
        "frames_per_ts": Counter(), "examples": [], "errors": [],
    }
    for p in paths:
        try:
            r = scan_time_file(p)
        except (OSError, ValueError, KeyError, pd.errors.ParserError) as exc:
            agg["errors"].append(f"{p.name}: {type(exc).__name__}: {exc}")
            continue
        agg["files"] += 1
        for k in ("rows", "frames", "plays", "uniq_time", "uniq_no_frac", "uniq_frac",
                  "unparsed", "pairs", "pairs_dt0", "pairs_dt_neg", "integer_secs"):
            agg[k] += r[k]
        for k in ("dt_counter", "frameid_gap_counter", "frames_per_ts"):
            agg[k].update(r[k])
        if len(agg["examples"]) < 3:
            agg["examples"].extend(r["examples"][: 3 - len(agg["examples"])])
        del r
        gc.collect()
    return agg


def process_sample(paths: list[Path], ctx) -> dict:
    team_vals: Counter = Counter()
    event_vals: Counter = Counter()
    per_file = []
    parts = []
    for p in paths:
        t0 = time.perf_counter()
        df = _read_full(p)
        team_vals.update(df["team"].astype(str).value_counts().to_dict())
        ev = df.drop_duplicates(KEYS + ["frameId", "event"])["event"].astype(str)
        event_vals.update(ev.value_counts().to_dict())
        agg = process_tracking_frame(df, ctx, None)
        del df
        gc.collect()
        per_file.append({"file": p.name, "plays": len(agg),
                         "seconds": time.perf_counter() - t0, "maxrss_mb": _maxrss_mb()})
        parts.append(agg)
    return {"team_vals": team_vals, "event_vals": event_vals, "per_file": per_file,
            "agg": pd.concat(parts, ignore_index=True)}


def passer_vs_qb(ctx) -> dict:
    roles = ctx.pff_roles
    pas = roles[roles["pff_role"].eq("Pass")]
    pos = pas["officialPosition"].fillna("<sin posición>")
    return {
        "n_pass_rows": len(pas),
        "n_plays": int(pas[KEYS].drop_duplicates().shape[0]),
        "qb_share": float(pas["officialPosition"].eq("QB").mean()) if len(pas) else float("nan"),
        "positions": pos.value_counts().to_dict(),
        "plays_multi_pass": int((pas.groupby(KEYS).size() > 1).sum()),
    }


def _fmt_counter(c: Counter, top: int = 8) -> str:
    return ", ".join(f"{k}: {v}" for k, v in c.most_common(top)) or "(vacío)"


def render(ctx, tscan, sample, qb, sample_paths, n_files, total_s) -> str:
    L: list[str] = []
    a = L.append
    agg = sample["agg"]
    a("# VERIFICATION_RUN")
    a("")
    a(f"Archivos de tracking: {n_files}. Muestra detallada: {len(sample_paths)} archivos "
      f"({', '.join(p.stem.replace('tracking_', '') for p in sample_paths)}).")
    a("")
    a("## 1. Formato crudo de `time` (los archivos completos, un archivo a la vez)")
    a("")
    pct = lambda x, y: (100.0 * x / y) if y else float("nan")
    a(f"- Archivos leídos: {tscan['files']}; con error: {len(tscan['errors'])}.")
    a(f"- Filas: {tscan['rows']:,}; frames distintos (jugada, frameId): {tscan['frames']:,}; jugadas: {tscan['plays']:,}.")
    a(f"- Ejemplos de valores crudos: {tscan['examples']}.")
    a(f"- Cadenas `time` distintas: {tscan['uniq_time']:,}. Sin fracción de segundo: {tscan['uniq_no_frac']:,} "
      f"({pct(tscan['uniq_no_frac'], tscan['uniq_time']):.2f}%). Con fracción: {tscan['uniq_frac']:,}. No parseables: {tscan['unparsed']:,}.")
    a(f"- Frames cuyo `time` cae en segundo entero: {tscan['integer_secs']:,} de {tscan['frames']:,} "
      f"({pct(tscan['integer_secs'], tscan['frames']):.2f}%).")
    a(f"- Pares de frames consecutivos: {tscan['pairs']:,}. Con dt = 0 s: {tscan['pairs_dt0']:,} "
      f"({pct(tscan['pairs_dt0'], tscan['pairs']):.2f}%). Con dt < 0: {tscan['pairs_dt_neg']:,}.")
    a(f"- Valores de dt entre frames consecutivos (s: pares): {_fmt_counter(tscan['dt_counter'])}.")
    a(f"- Saltos de `frameId` entre frames consecutivos (salto: pares): {_fmt_counter(tscan['frameid_gap_counter'])}.")
    a(f"- Frames por marca de tiempo distinta dentro de una jugada (frames: casos): {_fmt_counter(tscan['frames_per_ts'], 12)}.")
    if tscan["errors"]:
        a("- Errores: " + "; ".join(tscan["errors"][:5]))
    a("")
    a("**Conclusión sobre `time`:** ")
    frac_ok = tscan["uniq_frac"] == 0 and tscan["unparsed"] == 0
    if frac_ok:
        a("el formato es homogéneo (`YYYY-MM-DDTHH:MM:SSZ`, sin fracciones) y el parseo no pierde información. "
          "La columna `time` tiene resolución real de 1 s: cada marca de tiempo se repite en varios frames "
          "consecutivos (ver frames por marca). No es un problema de parseo; es una propiedad de los datos. "
          "Por eso `time_to_throw` se calcula con `frameId` a 10 Hz ((res − snap)/10) y `frame_dt_ok` exige "
          "`frameId` sin saltos de 1 y `time` no decreciente (D12).")
    else:
        a("hay valores con fracción o no parseables; ver cifras arriba. Revisar el parseo antes de usar `time`.")
    a("")
    a("## 2. Valores de `team` (muestra)")
    a("")
    a(f"- Valores: {_fmt_counter(sample['team_vals'], 40)}.")
    tv = set(sample["team_vals"]) - {"football", "nan"}
    ha = tv <= {"home", "away"}
    a(f"- Resultado: {'`home`/`away` (la normalización D8 con `games` es necesaria)' if ha else 'abreviaturas de equipo (D8 usa los valores tal cual)' if not (tv & {'home', 'away'}) else 'mezcla de home/away y abreviaturas'}.")
    a(f"- Eventos distintos por frame (muestra): {_fmt_counter(sample['event_vals'], 15)}.")
    a("")
    a("## 3. Rol PFF `Pass` frente a `officialPosition == QB` (todas las jugadas PFF)")
    a("")
    a(f"- Registros con `pff_role == Pass`: {qb['n_pass_rows']:,} en {qb['n_plays']:,} jugadas.")
    a(f"- Proporción con `officialPosition == QB`: {qb['qb_share']:.4f}.")
    a(f"- Posiciones de esos jugadores: {_fmt_counter(Counter(qb['positions']), 10)}.")
    a(f"- Jugadas con más de un `Pass`: {qb['plays_multi_pass']}.")
    a("")
    a("## 4. `frame_dt_ok`, `time_to_throw` (muestra procesada con `process_tracking_frame`)")
    a("")
    n = len(agg)
    a(f"- Jugadas en la muestra: {n:,}.")
    ok = float(agg["frame_dt_ok"].mean()) if n else float("nan")
    a(f"- `frame_dt_ok == 1`: {ok * 100:.1f}%.")
    ttt = agg["time_to_throw"].dropna()
    if len(ttt):
        a(f"- `time_to_throw` no nulo: {len(ttt):,}. Valores enteros: {(ttt % 1 == 0).mean() * 100:.1f}%. "
          f"Mín/mediana/máx: {ttt.min():.2f} / {ttt.median():.2f} / {ttt.max():.2f}.")
    both = agg.dropna(subset=["snap_frameId", "res_frameId"])
    if len(both):
        fr_ttt = (both["res_frameId"].astype("float64") - both["snap_frameId"].astype("float64")) / 10.0
        a(f"- `time_to_throw` coincide con (res − snap)/10 en el {((both['time_to_throw'] - fr_ttt).abs() < 1e-9).mean() * 100:.1f}% de las jugadas "
          f"(valores enteros: {(fr_ttt % 1 == 0).mean() * 100:.1f}%).")
    if "mean_dt_time" in agg.columns and n:
        md = agg["mean_dt_time"].dropna()
        a(f"- `mean_dt_time` (diagnóstico, dt medio por `time`): media {md.mean():.4f} s, mín/máx {md.min():.3f} / {md.max():.3f} s.")
    a("")
    a("## 5. Rendimiento")
    a("")
    pf = sample["per_file"]
    secs = [x["seconds"] for x in pf]
    a(f"- Tiempo por archivo (lectura + proceso, muestra): media {np.mean(secs):.2f} s, máx {np.max(secs):.2f} s. "
      f"Extrapolado a {n_files} archivos: ≈ {np.mean(secs) * n_files / 60:.1f} min.")
    a(f"- Pico de memoria (`ru_maxrss`, proceso completo, incluye tablas base y el escaneo de `time`): {_maxrss_mb():.0f} MB.")
    a(f"- Pico tras la muestra, archivo a archivo (MB): {', '.join(f'{x['maxrss_mb']:.0f}' for x in pf)}.")
    a(f"- Tiempo total de esta verificación: {total_s:.1f} s.")
    a("")
    return "\n".join(L) + "\n"


def write_atomic(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    t0 = time.perf_counter()
    try:
        paths = sorted(TRACKING_DIR.glob("tracking_*.csv"))
        if not paths:
            raise PipelineError(f"No hay archivos de tracking en {TRACKING_DIR}")
        tables = load_base_tables()
        run = RunReport()
        features = build_features(tables, run)
        ctx = build_context(tables, features)
        idx = np.unique(np.linspace(0, len(paths) - 1, SAMPLE_SIZE).round().astype(int))
        sample_paths = [paths[i] for i in idx]

        tscan = scan_all_time(paths)
        sample = process_sample(sample_paths, ctx)
        qb = passer_vs_qb(ctx)
        text = render(ctx, tscan, sample, qb, sample_paths, len(paths), time.perf_counter() - t0)
        write_atomic(text, OUTPUT_DIR / "VERIFICATION_RUN.md")
    except PipelineError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Error inesperado: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"Escrito {OUTPUT_DIR / 'VERIFICATION_RUN.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
