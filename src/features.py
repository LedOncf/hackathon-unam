"""Features del perfil Coach: constantes, errores y reporte de ejecución.

Este módulo no ejecuta código al importarse ni configura handlers de logging.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = PROJECT_ROOT / "data" / "nfl-big-data-bowl-regional-event-data" / "data"
TRACKING_DIR: Path = DATA_DIR / "tracking"
OUTPUT_DIR: Path = PROJECT_ROOT / "outputs"

ROLE_PASS_RUSH = "Pass Rush"
ROLE_PASS_BLOCK = "Pass Block"
ROLE_PASS = "Pass"

VALID_DOWNS = (1, 2, 3, 4)
SUCCESS_THRESHOLD = {1: 0.4, 2: 0.6, 3: 1.0, 4: 1.0}

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Error fatal del pipeline con mensaje claro."""


@dataclass
class RunReport:
    """Reporte_Ejecucion: contadores y avisos de la corrida."""

    counts: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def add(self, key: str, n: int = 1) -> None:
        self.counts[key] = self.counts.get(key, 0) + int(n)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)
        logger.warning(msg)
import pandas as pd

TABLE_FILES: dict[str, str] = {
    "plays": "plays.csv",
    "games": "games.csv",
    "players": "players.csv",
    "pff": "pffScoutingData.csv",
}
REQUIRED_PLAYS_COLUMNS = ("down", "prePenaltyPlayResult", "playResult")
REQUIRED_PFF_COLUMNS = (
    "gameId", "playId", "pff_role", "pff_hit", "pff_hurry", "pff_sack",
    "pff_beatenByDefender",
)
_REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "plays": REQUIRED_PLAYS_COLUMNS,
    "pff": REQUIRED_PFF_COLUMNS,
}


def load_base_tables(data_dir: Path = DATA_DIR) -> dict[str, pd.DataFrame]:
    """Carga plays, games, players y pff (solo lectura) y valida columnas.

    Lanza PipelineError con la ruta o la columna faltante. No escribe nada.
    """
    data_dir = Path(data_dir)
    paths = {key: data_dir / name for key, name in TABLE_FILES.items()}
    for path in paths.values():
        if not path.is_file():
            raise PipelineError(f"Archivo base no encontrado: {path}")
    tables: dict[str, pd.DataFrame] = {}
    for key, path in paths.items():
        try:
            df = pd.read_csv(path)
        except (OSError, ValueError, pd.errors.ParserError) as exc:
            raise PipelineError(f"No se pudo leer {path}: {exc}") from exc
        for col in _REQUIRED_COLUMNS.get(key, ()):
            if col not in df.columns:
                raise PipelineError(
                    f"Falta la columna requerida '{col}' en {path}"
                )
        tables[key] = df
    return tables


def filter_valid_plays(plays: pd.DataFrame) -> pd.DataFrame:
    """Conserva las jugadas con ``down`` en {1,2,3,4} y agrega ``no_penalty``.

    ``no_penalty`` es booleana sin nulos (``penaltyYards`` nulo). No modifica
    ``prePenaltyPlayResult`` ni ``playResult``.
    """
    down = pd.to_numeric(plays["down"], errors="coerce")
    mask = down.isin(VALID_DOWNS)
    out = plays.loc[mask].copy()
    if "penaltyYards" in out.columns:
        out["no_penalty"] = out["penaltyYards"].isna().astype(bool)
    else:
        out["no_penalty"] = True
    return out.reset_index(drop=True)


def compute_is_success(
    plays: pd.DataFrame, run: RunReport | None = None
) -> pd.DataFrame:
    """Agrega ``is_success`` (int8 en {0,1}) según down y ``yardsToGo``.

    Excluye y cuenta (``plays_excluded_is_success``) las jugadas con ``down``
    fuera de {1,2,3,4}, o ``yardsToGo``/``prePenaltyPlayResult`` nulos o no
    numéricos. Comparación con igualdad incluida; ``yardsToGo = 0`` es éxito
    si ``prePenaltyPlayResult >= 0``.
    """
    down = pd.to_numeric(plays["down"], errors="coerce")
    ytg = pd.to_numeric(plays["yardsToGo"], errors="coerce")
    res = pd.to_numeric(plays["prePenaltyPlayResult"], errors="coerce")
    valid = down.isin(VALID_DOWNS) & ytg.notna() & res.notna()
    n_excluded = int((~valid).sum())
    if run is not None and n_excluded:
        run.add("plays_excluded_is_success", n_excluded)
    threshold = down.map(SUCCESS_THRESHOLD).astype("float64") * ytg
    success = (res >= threshold) & valid
    out = plays.loc[valid].copy()
    out["is_success"] = success.loc[valid].astype("int8")
    return out.reset_index(drop=True)


def compute_pff_features(pff: pd.DataFrame) -> pd.DataFrame:
    """Métricas PFF por (gameId, playId).

    Compara ``pff_role`` con igualdad exacta y trata nulos de los flags como 0.
    """
    role = pff["pff_role"]
    rush = role.eq(ROLE_PASS_RUSH)
    block = role.eq(ROLE_PASS_BLOCK)

    def flag(col: str) -> pd.Series:
        return pd.to_numeric(pff[col], errors="coerce").fillna(0).eq(1)

    work = pd.DataFrame({
        "gameId": pff["gameId"],
        "playId": pff["playId"],
        "_rush": rush,
        "_block": block,
        "_press": rush & (flag("pff_hit") | flag("pff_hurry") | flag("pff_sack")),
        "_beaten": block & flag("pff_beatenByDefender"),
    })
    g = work.groupby(["gameId", "playId"], as_index=False).agg(
        n_rushers=("_rush", "sum"),
        n_blockers=("_block", "sum"),
        any_pressure=("_press", "max"),
        any_beaten=("_beaten", "max"),
    )
    g["protection_advantage"] = g["n_blockers"] - g["n_rushers"]
    g["is_blitz"] = g["n_rushers"] >= 5
    for col in ("n_rushers", "n_blockers", "protection_advantage"):
        g[col] = g[col].astype("Int16")
    for col in ("is_blitz", "any_pressure", "any_beaten"):
        g[col] = g[col].astype("int8").astype("Int8")
    return g[[
        "gameId", "playId", "n_rushers", "n_blockers", "protection_advantage",
        "is_blitz", "any_pressure", "any_beaten",
    ]]


def attach_positions(pff: pd.DataFrame, players: pd.DataFrame) -> pd.DataFrame:
    """Left join por ``nflId`` para agregar ``officialPosition``.

    No cambia el número de filas de ``pff``.
    """
    pos = (
        players[["nflId", "officialPosition"]]
        .drop_duplicates(subset="nflId", keep="first")
    )
    return pff.merge(pos, on="nflId", how="left")


_PLAY_COLUMNS = (
    "gameId", "playId", "quarter", "down", "yardsToGo", "possessionTeam",
    "defensiveTeam", "yardlineSide", "yardlineNumber", "gameClock",
    "preSnapHomeScore", "preSnapVisitorScore", "passResult",
    "prePenaltyPlayResult", "playResult", "penaltyYards", "no_penalty",
    "offenseFormation", "personnelO", "personnelD", "defendersInBox",
    "dropBackType", "pff_playAction", "pff_passCoverage",
    "pff_passCoverageType", "is_success",
)
_GAME_COLUMNS = ("gameId", "season", "week", "gameDate", "homeTeamAbbr",
                 "visitorTeamAbbr")


def build_features(
    tables: dict[str, pd.DataFrame] | None = None,
    run: RunReport | None = None,
) -> pd.DataFrame:
    """Tabla de features: una fila por (gameId, playId) válida."""
    if tables is None:
        tables = load_base_tables()
    plays = compute_is_success(filter_valid_plays(tables["plays"]), run)
    plays = plays.drop_duplicates(subset=["gameId", "playId"], keep="first")
    plays = plays[[c for c in _PLAY_COLUMNS if c in plays.columns]]

    games = tables["games"]
    games = games[[c for c in _GAME_COLUMNS if c in games.columns]]
    games = games.drop_duplicates(subset="gameId", keep="first")

    pff_feats = compute_pff_features(tables["pff"])

    out = plays.merge(games, on="gameId", how="left")
    out = out.merge(pff_feats, on=["gameId", "playId"], how="left")
    return out.reset_index(drop=True)
