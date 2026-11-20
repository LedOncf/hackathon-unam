"""Decisión y texto del Verdict (req. 7, 3.9).

Función pura: no lee datos. Recibe los tamaños de grupo, el Effect_pp y su
intervalo ya calculados por ``recommend_service`` (los mismos valores que se
devuelven en la comparativa Play Action, para que el signo coincida, 7.9).
"""

from __future__ import annotations

from typing import Optional, Sequence

MIN_N = 30
MAX_TEXT_LEN = 280
CLARIFICATION = "Éxito por down y distancia; sin EPA."
EMPTY_SUBSET_TEXT = "No hay jugadas para la situación elegida."
RED_ZONE = "Red Zone"

LLAMAR_PLAY_ACTION = "LLAMAR_PLAY_ACTION"
EVITAR_PLAY_ACTION = "EVITAR_PLAY_ACTION"
SIN_VENTAJA_CLARA = "SIN_VENTAJA_CLARA"
MUESTRA_INSUFICIENTE = "MUESTRA_INSUFICIENTE"
VERDICT_CODES = (
    LLAMAR_PLAY_ACTION,
    EVITAR_PLAY_ACTION,
    SIN_VENTAJA_CLARA,
    MUESTRA_INSUFICIENTE,
)


def _abs1(x: float) -> str:
    return f"{abs(round(float(x), 1)):.1f}"


def _signed1(x: float) -> str:
    r = round(float(x), 1)
    if r == 0:
        r = 0.0  # evita "-0.0"
    return f"{'-' if r < 0 else '+'}{abs(r):.1f}"


def _round1(x: Optional[float]) -> Optional[float]:
    if x is None:
        return None
    r = round(float(x), 1)
    return 0.0 if r == 0 else r


def _blitz_note(
    n_blitz: Optional[int], n_standard: Optional[int], pressure_pp: Optional[float]
) -> str:
    if (
        n_blitz is None
        or n_standard is None
        or pressure_pp is None
        or n_blitz < MIN_N
        or n_standard < MIN_N
    ):
        return ""
    return f"Blitz: presión {_signed1(pressure_pp)} pp frente a cobertura estándar."


def build_verdict(
    subset_n: int,
    n_pa: int,
    n_trad: int,
    effect_pp: Optional[float],
    effect_pp_ci: Optional[Sequence[Optional[float]]],
    coverage: Optional[str] = None,
    n_blitz: Optional[int] = None,
    n_standard: Optional[int] = None,
    pressure_pp: Optional[float] = None,
) -> dict:
    """Devuelve ``{"code", "text", "effect_pp", "effect_pp_ci"}``.

    - ``effect_pp`` y ``effect_pp_ci`` (``[lo, hi]``) vienen de la comparativa
      Play Action (Play Action menos tradicional); pueden ser ``None``.
    - ``coverage``: cobertura del filtro (``"Red Zone"`` activa el titular propio).
    - ``n_blitz``, ``n_standard``, ``pressure_pp``: para la nota de blitz (7.7).
    """
    lo = hi = None
    if effect_pp_ci is not None and len(effect_pp_ci) == 2:
        lo, hi = effect_pp_ci
    has_effect = effect_pp is not None and lo is not None and hi is not None

    note = _blitz_note(n_blitz, n_standard, pressure_pp)

    # A8: subset vacío
    if subset_n == 0:
        headline = EMPTY_SUBSET_TEXT
        code = MUESTRA_INSUFICIENTE
        has_effect = False
        note = ""
    elif n_pa < MIN_N or n_trad < MIN_N:
        code = MUESTRA_INSUFICIENTE
        headline = (
            f"MUESTRA INSUFICIENTE: n = {n_pa} con play action y n = {n_trad} "
            f"sin play action (mínimo {MIN_N} por grupo)."
        )
        if n_pa == 0 or n_trad == 0:
            has_effect = False
    elif not has_effect:
        # Entrada inconsistente (n >= 30 sin efecto): no se puede decidir.
        code = MUESTRA_INSUFICIENTE
        headline = (
            f"MUESTRA INSUFICIENTE: n = {n_pa} con play action y n = {n_trad} "
            f"sin play action; no se pudo calcular la diferencia."
        )
    elif lo > 0:
        code = LLAMAR_PLAY_ACTION
        headline = f"LLAMAR PLAY ACTION (+{_abs1(effect_pp)} pp de éxito esperado)"
    elif hi < 0:
        code = EVITAR_PLAY_ACTION
        prefix = (
            "EVITAR PLAY ACTION EN RED ZONE"
            if coverage == RED_ZONE
            else "EVITAR PLAY ACTION"
        )
        headline = f"{prefix} ({_abs1(effect_pp)} pp menos éxito)"
    else:
        code = SIN_VENTAJA_CLARA
        headline = (
            f"SIN VENTAJA CLARA: la diferencia de {_signed1(effect_pp)} pp "
            "no es concluyente (el intervalo incluye 0)."
        )

    def compose(with_note: bool) -> str:
        parts = [headline]
        if with_note and note:
            parts.append(note)
        parts.append(CLARIFICATION)
        return " ".join(parts)

    text = compose(True)
    if len(text) > MAX_TEXT_LEN:
        text = compose(False)
    if len(text) > MAX_TEXT_LEN:  # no debería ocurrir; garantía dura de 7.1
        text = text[: MAX_TEXT_LEN - 1] + "…"

    return {
        "code": code,
        "text": text,
        "effect_pp": _round1(effect_pp) if has_effect else None,
        "effect_pp_ci": [_round1(lo), _round1(hi)] if has_effect else None,
    }
