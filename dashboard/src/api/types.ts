// Tipos de las respuestas de la API. Reflejan los modelos de backend/schemas.py.
export type Role = 'QB' | 'Pass Route' | 'Pass Block' | 'Pass Rush' | 'Coverage' | 'LB'
export type VerdictCode =
  | 'LLAMAR_PLAY_ACTION'
  | 'EVITAR_PLAY_ACTION'
  | 'SIN_VENTAJA_CLARA'
  | 'MUESTRA_INSUFICIENTE'
export type Focus = 'bite' | 'pa_fallida' | 'blitz_exitoso'
/** Par de intervalo [lo, hi] o null. */
export type Pair = [number, number] | null

export interface YardsToGoBucket { name: string; min: number; max: number | null }

export interface FiltersResponse {
  down: number[]
  pff_passCoverage: string[]
  pff_passCoverageType: string[]
  offenseFormation: string[]
  defendersInBox: number[]
  yards_to_go_buckets: YardsToGoBucket[]
}

export interface MeanStat { mean: number | null; n_used: number }

export interface PaGroup {
  n: number
  successes: number
  success_rate: number | null
  ci: Pair
  mean_yards: number | null
  lb_bite: MeanStat
  insufficient: boolean
  label: string | null
}

export interface BlitzGroup {
  n: number
  success_rate: number | null
  ci: Pair
  any_pressure_pct: number | null
  time_to_throw: MeanStat
  min_rusher_dist: MeanStat
  insufficient: boolean
  label: string | null
}

export interface PlayActionBlock {
  play_action: PaGroup
  traditional: PaGroup
  effect_pp: number | null
  effect_pp_ci: Pair
  effect_yards: number | null
}

export interface BlitzBlock {
  blitz: BlitzGroup
  standard: BlitzGroup
  effect_pp: number | null
  effect_pp_ci: Pair
  pressure_pp: number | null
  time_to_throw_diff: number | null
  min_rusher_dist_diff: number | null
}

export interface LbBiteRow {
  range: string
  lo: number | null
  hi: number | null
  n: number
  n_pa: number
  n_trad: number
  pa_success_rate: number | null
  trad_success_rate: number | null
  pa_pressure_rate: number | null
  trad_pressure_rate: number | null
  insufficient: boolean
  label: string | null
}

export interface ProtectionRow {
  category: string
  n: number
  any_pressure: number | null
  success_rate: number | null
  insufficient: boolean
  label: string | null
}

export interface Physics { lb_bite_table: LbBiteRow[]; protection_table: ProtectionRow[] }

export interface Verdict {
  code: VerdictCode
  text: string
  effect_pp: number | null
  effect_pp_ci: Pair
}

export interface RecommendResponse {
  subset_n: number
  filter: {
    down: string | null
    yards_to_go_bucket: string | null
    coverage: string | null
    formation: string | null
    defenders_in_box: number | null
  }
  play_action: PlayActionBlock
  blitz: BlitzBlock
  physics: Physics
  verdict: Verdict
}

export interface TrackPoint {
  frameId: number
  x_norm: number
  y_norm: number
  s: number | null
  a: number | null
}

export interface BallPoint { frameId: number; x_norm: number; y_norm: number }

export interface PlayerTrack {
  nflId: number
  role: Role
  position: string | null
  label: string
  side: 'offense' | 'defense'
  is_lb: boolean
  track: TrackPoint[]
}

export interface PlayMeta {
  id: string
  gameId: number
  playId: number
  week: number | null
  offense: string | null
  defense: string | null
  down: number | null
  yards_to_go: number | null
  coverage: string | null
  formation: string | null
  play_action: number | null
  is_blitz: number | null
  any_pressure: number | null
  is_success: number | null
  lb_bite_yards: number | null
  min_rusher_dist_at_throw: number | null
  time_to_throw: number | null
}

export interface SamplePlayResponse {
  preferred: boolean
  play: PlayMeta
  snap_frame: number
  pass_forward_frame: number
  frames: number[]
  players: PlayerTrack[]
  ball: BallPoint[]
}

/** Cuerpo de error de la API. */
export interface ApiErrorBody { detail: string; invalid?: string[] }
