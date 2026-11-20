// "" significa "Todos".
export interface Situation {
  down: string
  ytg: string
  coverage: string
  formation: string
  box: string
}

export const INITIAL_SITUATION: Situation = { down: '', ytg: '', coverage: '', formation: '', box: '' }

/** Construye la cadena de consulta omitiendo valores vacíos. Devuelve '' si no hay parámetros. */
export function toQuery(s: Situation, extra: Record<string, string | undefined> = {}): string {
  const p = new URLSearchParams()
  const pairs: Record<string, string | undefined> = {
    down: s.down,
    yards_to_go_bucket: s.ytg,
    coverage: s.coverage,
    formation: s.formation,
    defenders_in_box: s.box,
    ...extra,
  }
  for (const [k, v] of Object.entries(pairs)) {
    if (v !== undefined && v !== '') p.set(k, v)
  }
  return p.toString()
}

/** URL relativa (sin diagonal inicial) de un endpoint con la situación. */
export function apiUrl(endpoint: string, s?: Situation, extra?: Record<string, string | undefined>): string {
  const q = s ? toQuery(s, extra) : ''
  return q ? `api/${endpoint}?${q}` : `api/${endpoint}`
}
