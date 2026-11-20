"""Rutas absolutas y constantes del backend."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# La copia dentro de backend/ viaja siempre con el código desplegado; la de
# outputs/ es la que genera `python -m src.analyze` y tiene prioridad si existe.
PLAYS_CSV_CANDIDATES = (
    PROJECT_ROOT / "outputs" / "plays_enriched.csv",
    Path(__file__).resolve().parent / "assets" / "plays_enriched.csv",
)
PLAYS_CSV = next((p for p in PLAYS_CSV_CANDIDATES if p.is_file()), PLAYS_CSV_CANDIDATES[0])
DATA_DIR = PROJECT_ROOT / "data" / "nfl-big-data-bowl-regional-event-data" / "data"
TRACKING_DIR = DATA_DIR / "tracking"
DIST_DIR = PROJECT_ROOT / "dashboard" / "dist"

MIN_N = 30
Z95 = 1.96
