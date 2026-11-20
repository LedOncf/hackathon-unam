"""PlaysStore: carga única de plays_enriched.csv con columnas derivadas."""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import HTTPException

from backend import config

log = logging.getLogger("backend.store")

REQUIRED_COLUMNS = [
    "gameId", "playId", "down", "yardsToGo", "possessionTeam", "defensiveTeam",
    "homeTeamAbbr", "visitorTeamAbbr", "week", "offenseFormation", "defendersInBox",
    "pff_playAction", "pff_passCoverage", "pff_passCoverageType",
    "prePenaltyPlayResult", "is_success", "is_blitz", "any_pressure",
    "protection_advantage", "time_to_throw", "min_rusher_dist_at_throw",
    "lb_bite_yards", "snap_frameId", "res_frameId", "has_tracking",
]
MANDATORY_NOT_NULL = ["pff_playAction", "is_blitz", "is_success"]

NO_DATA_MESSAGE = (
    "Los datos de jugadas no están disponibles. Revisa outputs/plays_enriched.csv."
)


def _bite_bin(s: pd.Series) -> pd.Series:
    """0..3 con bordes 0.10, 0.69, 1.16 ([a, b)); -1 si es nulo."""
    out = np.digitize(s.to_numpy(dtype=float), [0.10, 0.69, 1.16], right=False)
    return pd.Series(np.where(s.isna().to_numpy(), -1, out), index=s.index, dtype="int64")


def _prot_cat(s: pd.Series) -> pd.Series:
    def f(v):
        if pd.isna(v):
            return None
        if v <= -1:
            return "-2 a -1"
        if v >= 3:
            return "3 a 6"
        return str(int(v))
    return s.map(f).astype("object")


def _ytg_bucket(s: pd.Series) -> pd.Series:
    return pd.Series(
        np.where(s >= 8, "larga", np.where(s >= 4, "media", np.where(s >= 1, "corta", None))),
        index=s.index, dtype="object",
    )


def _sorted_text(values) -> list[str]:
    vals = {str(v) for v in values if pd.notna(v) and str(v).strip() != ""}
    return sorted(vals, key=lambda t: (t.lower(), t))


def _sorted_ints(values) -> list[int]:
    return sorted({int(v) for v in values if pd.notna(v)})


class PlaysStore:
    def __init__(self) -> None:
        self.df: pd.DataFrame | None = None
        self.error: str | None = None
        self.filter_values: dict[str, list] = {}

    def load(self, path: Path | None = None) -> None:
        """Carga el CSV una vez. Nunca lanza: deja el motivo en `self.error`."""
        path = Path(path) if path is not None else config.PLAYS_CSV
        self.df, self.filter_values, self.error = None, {}, None
        try:
            if not path.is_file():
                raise FileNotFoundError(f"No existe el archivo {path}")
            raw = pd.read_csv(path)
            missing = [c for c in REQUIRED_COLUMNS if c not in raw.columns]
            if missing:
                raise ValueError(f"Faltan columnas en {path.name}: {', '.join(missing)}")
            self.df = self._prepare(raw)
            self.filter_values = self._compute_filter_values(self.df)
        except Exception as exc:  # noqa: BLE001 - la carga no debe terminar el proceso
            self.df, self.filter_values = None, {}
            self.error = f"{NO_DATA_MESSAGE} Detalle: {exc}"
            log.error("No se pudo cargar %s: %s", path, exc)

    @staticmethod
    def _prepare(raw: pd.DataFrame) -> pd.DataFrame:
        df = raw.copy()
        n_null = int(df[MANDATORY_NOT_NULL].isna().any(axis=1).sum())
        if n_null:
            log.warning("Se excluyen %d jugadas con nulos en %s", n_null, MANDATORY_NOT_NULL)
        keep = df["down"].isin([1, 2, 3, 4]) & df[MANDATORY_NOT_NULL].notna().all(axis=1)
        df = df.loc[keep].reset_index(drop=True)
        df["ytg_bucket"] = _ytg_bucket(df["yardsToGo"])
        df["box_int"] = df["defendersInBox"].round().astype("Int64")
        df["bite_bin"] = _bite_bin(df["lb_bite_yards"])
        df["prot_cat"] = _prot_cat(df["protection_advantage"])
        df["play_id"] = df["gameId"].astype("int64").astype(str) + "-" + df["playId"].astype("int64").astype(str)
        return df

    @staticmethod
    def _compute_filter_values(df: pd.DataFrame) -> dict[str, list]:
        return {
            "down": _sorted_ints(df["down"]),
            "pff_passCoverage": _sorted_text(df["pff_passCoverage"]),
            "pff_passCoverageType": _sorted_text(df["pff_passCoverageType"]),
            "offenseFormation": _sorted_text(df["offenseFormation"]),
            "defendersInBox": _sorted_ints(df["box_int"]),
        }


store = PlaysStore()


def require_store() -> PlaysStore:
    """Dependencia FastAPI: 503 en español si no hay datos."""
    if store.df is None:
        raise HTTPException(status_code=503, detail=NO_DATA_MESSAGE)
    return store
