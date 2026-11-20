"""Utilidades de pruebas de propiedades sin hypothesis."""
from __future__ import annotations

from typing import Callable

import numpy as np


def run_property(seed: int, n_iter: int, fn: Callable[[np.random.Generator], None]) -> None:
    """Ejecuta `fn(rng)` n_iter (>= 100) veces con un generador sembrado.

    Si una iteración falla, imprime semilla e iteración y relanza la excepción.
    """
    n_iter = max(int(n_iter), 100)
    rng = np.random.default_rng(seed)
    for i in range(n_iter):
        try:
            fn(rng)
        except Exception:
            print(f"Property failed: seed={seed}, iteration={i}")
            raise
