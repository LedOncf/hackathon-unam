"""Estadística del Backend: envoltorios de `src.analyze` y redondeo.

Una sola fuente de verdad: Wilson y Newcombe se calculan con
`src.analyze.wilson_ci` y `src.analyze.diff_props_ci` (z = 1.96). Este módulo
solo convierte a porcentaje o puntos porcentuales y redondea una única vez, al
devolver, para que el signo de un efecto redondeado coincida con el de la
diferencia de tasas redondeadas.
"""

from __future__ import annotations

import math

import pandas as pd

from src.analyze import diff_props_ci, wilson_ci


def _round(x, ndigits: int):
    """Redondea con None-safe; no finitos dan None y -0.0 se vuelve 0.0."""
    if x is None:
        return None
    f = float(x)
    if not math.isfinite(f):
        return None
    r = round(f, ndigits)
    return 0.0 if r == 0 else r


def r1(x):
    """Redondea a 1 decimal (None-safe, sin -0.0)."""
    return _round(x, 1)


def r2(x):
    """Redondea a 2 decimales (None-safe, sin -0.0)."""
    return _round(x, 2)


def r3(x):
    """Redondea a 3 decimales (None-safe, sin -0.0)."""
    return _round(x, 3)


def wilson_pct(k: int, n: int) -> tuple[float, float] | None:
    """IC de Wilson al 95% en porcentaje (0 a 100, 1 decimal). None si n <= 0."""
    ci = wilson_ci(int(k), int(n))
    if ci is None:
        return None
    return r1(ci[0] * 100.0), r1(ci[1] * 100.0)


def newcombe_diff_pp(
    k1: int, n1: int, k0: int, n0: int
) -> tuple[float, float, float] | None:
    """(diferencia, inferior, superior) del grupo 1 menos el 0, en pp con 1 decimal.

    Devuelve None si algún grupo tiene n < 2 (sin IC disponible).
    """
    d = diff_props_ci(int(k1), int(n1), int(k0), int(n0))
    if d.diff is None or d.lo is None or d.hi is None:
        return None
    return r1(d.diff * 100.0), r1(d.lo * 100.0), r1(d.hi * 100.0)


def mean_or_none(series, ndigits: int | None = 2) -> tuple[float | None, int]:
    """(media, n de valores no nulos), excluyendo solo nulos y no finitos.

    Sin valores devuelve (None, 0). `ndigits=None` devuelve la media sin
    redondear, para calcular diferencias antes de redondear.
    """
    s = pd.to_numeric(pd.Series(series), errors="coerce").astype("float64")
    s = s[s.notna() & s.map(math.isfinite)]
    n = int(s.size)
    if n == 0:
        return None, 0
    m = float(s.mean())
    return (m if ndigits is None else _round(m, ndigits)), n
