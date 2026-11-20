// Formato de números para la interfaz. Los valores nulos se muestran como guion (en dash).
export const DASH = '–'

const isNum = (v: number | null | undefined): v is number =>
  typeof v === 'number' && Number.isFinite(v)

export const fmt1 = (v: number | null | undefined): string => (isNum(v) ? v.toFixed(1) : DASH)
export const fmt2 = (v: number | null | undefined): string => (isNum(v) ? v.toFixed(2) : DASH)
/** Porcentaje ya expresado de 0 a 100. */
export const pct = (v: number | null | undefined): string => (isNum(v) ? `${v.toFixed(1)}%` : DASH)
/** Proporción de 0 a 1 mostrada como porcentaje. */
export const pctFromRatio = (v: number | null | undefined): string =>
  isNum(v) ? `${(v * 100).toFixed(1)}%` : DASH
/** Diferencia con signo explícito. */
export const signed1 = (v: number | null | undefined): string =>
  isNum(v) ? `${v > 0 ? '+' : ''}${v.toFixed(1)}` : DASH
export const dash = (v: string | number | null | undefined): string =>
  v === null || v === undefined || v === '' ? DASH : String(v)
