"""Situation_Filter: validación de parámetros (422) y máscara del Subset."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping

import pandas as pd

VALID_DOWNS = ("1", "2", "3", "4", "3-4")
VALID_BUCKETS = ("corta", "media", "larga")
_INT_RE = re.compile(r"^\d+(\.0+)?$")


@dataclass(frozen=True)
class SituationFilter:
    down: str | None = None  # "1","2","3","4","3-4"
    yards_to_go_bucket: str | None = None
    coverage: str | None = None
    formation: str | None = None
    defenders_in_box: int | None = None


class SituationError(Exception):
    """Parámetros inválidos. Se responde HTTP 422 con {"detail", "invalid"}."""

    status_code = 422

    def __init__(self, detail: str, invalid: list[str]) -> None:
        super().__init__(detail)
        self.detail = detail
        self.invalid = invalid

    def body(self) -> dict:
        return {"detail": self.detail, "invalid": self.invalid}

    def to_response(self):
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=self.status_code, content=self.body())


def _blank(v: str | None) -> bool:
    return v is None or v == ""


def parse_situation(raw: Mapping[str, str | None], store) -> SituationFilter:
    """Valida todos los parámetros; si alguno es inválido lanza SituationError
    nombrando todos los inválidos."""
    fv = getattr(store, "filter_values", None) or {}
    invalid: list[tuple[str, str]] = []

    down = raw.get("down")
    if _blank(down):
        down = None
    elif down not in VALID_DOWNS:
        invalid.append(("down", str(down)))

    bucket = raw.get("yards_to_go_bucket")
    if _blank(bucket):
        bucket = None
    elif bucket not in VALID_BUCKETS:
        invalid.append(("yards_to_go_bucket", str(bucket)))

    coverage = raw.get("coverage")
    if _blank(coverage):
        coverage = None
    elif coverage not in fv.get("pff_passCoverage", []):
        invalid.append(("coverage", str(coverage)))

    formation = raw.get("formation")
    if _blank(formation):
        formation = None
    elif formation not in fv.get("offenseFormation", []):
        invalid.append(("formation", str(formation)))

    box_raw = raw.get("defenders_in_box")
    box: int | None = None
    if not _blank(box_raw):
        box_s = str(box_raw)
        if _INT_RE.match(box_s) and int(float(box_s)) in fv.get("defendersInBox", []):
            box = int(float(box_s))
        else:
            invalid.append(("defenders_in_box", box_s))

    if invalid:
        names = [n for n, _ in invalid]
        parts = ", ".join(f"{n} (valor '{v}')" for n, v in invalid)
        raise SituationError(f"Parámetro(s) inválido(s): {parts}.", names)

    return SituationFilter(down, bucket, coverage, formation, box)


def subset_mask(df: pd.DataFrame, f: SituationFilter) -> pd.Series:
    """Máscara booleana del Subset. Siempre excluye `down` fuera de 1 a 4."""
    mask = df["down"].isin([1, 2, 3, 4])
    if f.down is not None:
        if f.down == "3-4":
            mask &= df["down"].isin([3, 4])
        else:
            mask &= df["down"] == int(f.down)
    if f.yards_to_go_bucket is not None:
        mask &= df["ytg_bucket"] == f.yards_to_go_bucket
    if f.coverage is not None:
        mask &= df["pff_passCoverage"] == f.coverage
    if f.formation is not None:
        mask &= df["offenseFormation"] == f.formation
    if f.defenders_in_box is not None:
        mask &= (df["box_int"] == f.defenders_in_box).fillna(False).astype(bool)
    return mask
