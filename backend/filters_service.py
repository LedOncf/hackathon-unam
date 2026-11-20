"""Filter_Service: GET /api/filters (valores únicos precalculados en el store)."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.store import PlaysStore, require_store

router = APIRouter()

YARDS_TO_GO_BUCKETS = [
    {"name": "corta", "min": 1, "max": 3},
    {"name": "media", "min": 4, "max": 7},
    {"name": "larga", "min": 8, "max": None},
]


def build_filters(store: PlaysStore) -> dict:
    fv = store.filter_values
    return {
        "down": list(fv.get("down", [])),
        "pff_passCoverage": list(fv.get("pff_passCoverage", [])),
        "pff_passCoverageType": list(fv.get("pff_passCoverageType", [])),
        "offenseFormation": list(fv.get("offenseFormation", [])),
        "defendersInBox": [int(v) for v in fv.get("defendersInBox", [])],
        "yards_to_go_buckets": [dict(b) for b in YARDS_TO_GO_BUCKETS],
    }


@router.get("/filters")
def get_filters(store: PlaysStore = Depends(require_store)) -> dict:
    return build_filters(store)
