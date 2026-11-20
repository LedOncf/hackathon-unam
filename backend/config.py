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
FULL_DATA_DIR = PROJECT_ROOT / "data" / "nfl-big-data-bowl-regional-event-data" / "data"
SAMPLE_DIR = Path(__file__).resolve().parent / "assets" / "tracking_sample"

# Con los datos completos (local) se usan los 122 archivos de tracking. Si no
# están (la plataforma solo despliega backend/), la pizarra usa una muestra de
# jugadas reales recortadas, y solo ofrece las jugadas incluidas en ella.
if (FULL_DATA_DIR / "tracking").is_dir() and any((FULL_DATA_DIR / "tracking").glob("tracking_*.csv")):
    DATA_DIR = FULL_DATA_DIR
    SAMPLE_PLAY_IDS = None
else:
    DATA_DIR = SAMPLE_DIR
    _manifest = SAMPLE_DIR / "manifest.csv"
    SAMPLE_PLAY_IDS = (
        set(_manifest.read_text(encoding="utf-8").split()[1:]) if _manifest.is_file() else set()
    )
TRACKING_DIR = DATA_DIR / "tracking"
DIST_DIR = PROJECT_ROOT / "dashboard" / "dist"

MIN_N = 30
Z95 = 1.96
