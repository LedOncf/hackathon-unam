"""Estadística del Backend: Wilson, Newcombe (z = 1.96) y redondeo.

Autocontenido: la plataforma solo empaqueta `backend/` y no incluye el paquete
`src/`, así que estas funciones replican (con la misma fórmula) las de
`src/analyze.py`. Convierte a porcentaje o puntos porcentuales y redondea una
única vez, al devolver, para que el signo de un efecto redondeado coincida con
el de la diferencia de tasas redondeadas.
"""

from __future__ import annotations

import math
from types import SimpleNamespace

import pandas as pd

Z95 = 1.96


def wilson_ci(k: int, n: int, z: float = Z95) -> tuple[float, float] | None:
    """IC de Wilson para una proporción. None si n <= 0."""
    if n <= 0:
        return None
    p = k / n
    z2 = z * z
    den = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / den
    half = z * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n)) / den
    return max(0.0, center - half), min(1.0, center + half)


def diff_props_ci(k1: int, n1: int, k0: int, n0: int, z: float = Z95) -> SimpleNamespace:
    """Diferencia de proporciones (grupo 1 menos 0), IC híbrido de Newcombe.

    Devuelve un objeto con `diff`, `lo` y `hi` en proporción (no pp). Con un
    grupo vacío todo es None; con n < 2 en algún grupo solo hay `diff`.
    """
    out = SimpleNamespace(diff=None, lo=None, hi=None)
    if n1 <= 0 or n0 <= 0:
        return out
    p1, p0 = k1 / n1, k0 / n0
    out.diff = p1 - p0
    if n1 < 2 or n0 < 2:
        return out
    l1, u1 = wilson_ci(k1, n1, z)  # type: ignore[misc]
    l0, u0 = wilson_ci(k0, n0, z)  # type: ignore[misc]
    out.lo = out.diff - math.sqrt((p1 - l1) ** 2 + (u0 - p0) ** 2)
    out.hi = out.diff + math.sqrt((u1 - p1) ** 2 + (p0 - l0) ** 2)
    return out


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
