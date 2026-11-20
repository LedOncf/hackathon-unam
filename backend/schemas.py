"""Modelos Pydantic de GET /api/recommend.

Unidades: los porcentajes de grupo (`success_rate`, `ci`, `any_pressure_pct`,
`effect_pp`, `pressure_pp`) van de 0 a 100 con 1 decimal. Las medias de yardas y
segundos llevan 2 decimales. Las tablas de física usan proporciones 0.000 a
1.000. Los intervalos son listas `[lo, hi]`.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel

VerdictCode = Literal[
    "LLAMAR_PLAY_ACTION", "EVITAR_PLAY_ACTION", "SIN_VENTAJA_CLARA", "MUESTRA_INSUFICIENTE"
]


class MeanStat(BaseModel):
    mean: Optional[float] = None
    n_used: int = 0


class PaGroup(BaseModel):
    n: int
    successes: int
    success_rate: Optional[float] = None  # %
    ci: Optional[list[float]] = None  # [lo, hi] en %
    mean_yards: Optional[float] = None
    lb_bite: MeanStat
    insufficient: bool
    label: Optional[str] = None


class BlitzGroup(BaseModel):
    n: int
    success_rate: Optional[float] = None  # %
    ci: Optional[list[float]] = None  # [lo, hi] en %
    any_pressure_pct: Optional[float] = None  # %
    time_to_throw: MeanStat
    min_rusher_dist: MeanStat
    insufficient: bool
    label: Optional[str] = None


class PlayActionBlock(BaseModel):
    play_action: PaGroup
    traditional: PaGroup
    effect_pp: Optional[float] = None
    effect_pp_ci: Optional[list[float]] = None
    effect_yards: Optional[float] = None


class BlitzBlock(BaseModel):
    blitz: BlitzGroup
    standard: BlitzGroup
    effect_pp: Optional[float] = None
    effect_pp_ci: Optional[list[float]] = None
    pressure_pp: Optional[float] = None
    time_to_throw_diff: Optional[float] = None
    min_rusher_dist_diff: Optional[float] = None


class LbBiteRow(BaseModel):
    range: str
    lo: Optional[float] = None
    hi: Optional[float] = None
    n: int
    n_pa: int
    n_trad: int
    pa_success_rate: Optional[float] = None  # proporción 0..1
    trad_success_rate: Optional[float] = None  # proporción 0..1
    pa_pressure_rate: Optional[float] = None  # proporción 0..1 de any_pressure (aditivo, req. 12.7)
    trad_pressure_rate: Optional[float] = None  # proporción 0..1 de any_pressure (aditivo, req. 12.7)
    insufficient: bool
    label: Optional[str] = None


class ProtectionRow(BaseModel):
    category: str
    n: int
    any_pressure: Optional[float] = None  # proporción 0..1
    success_rate: Optional[float] = None  # proporción 0..1
    insufficient: bool
    label: Optional[str] = None


class Physics(BaseModel):
    lb_bite_table: list[LbBiteRow]
    protection_table: list[ProtectionRow]


class Verdict(BaseModel):
    code: VerdictCode
    text: str
    effect_pp: Optional[float] = None
    effect_pp_ci: Optional[list[float]] = None


class RecommendResponse(BaseModel):
    subset_n: int
    filter: dict
    play_action: PlayActionBlock
    blitz: BlitzBlock
    physics: Physics
    verdict: Verdict
