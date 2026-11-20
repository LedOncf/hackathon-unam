"""Rutas absolutas y constantes del backend."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLAYS_CSV = PROJECT_ROOT / "outputs" / "plays_enriched.csv"
DATA_DIR = PROJECT_ROOT / "data" / "nfl-big-data-bowl-regional-event-data" / "data"
TRACKING_DIR = DATA_DIR / "tracking"
DIST_DIR = PROJECT_ROOT / "dashboard" / "dist"

MIN_N = 30
Z95 = 1.96
