import { Bar, BarChart, CartesianGrid, Cell, ErrorBar, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { Pair, RecommendResponse } from '../api/types'
import { DASH, fmt1, fmt2 } from '../lib/format'

export const N_MIN = 30
export const AVISO_MUESTRA = 'Muestra insuficiente (n < 30)'
/** Opacidad de barras con muestra insuficiente (entre 0.3 y 0.5). */
export const OPACIDAD_INSUFICIENTE = 0.4

const TEXTO = '#cbd5e1' // slate-300

export interface Serie {
  key: string
  name: string
  color: string
}

/** Fila de datos: una categoría con un valor por serie. */
export interface Fila {
  name: string
  [k: string]: string | number | boolean | null
}

/** Construye los campos de una serie dentro de una fila. */
export function campos(
  key: string,
  value: number | null,
  n: number,
  ci: Pair = null,
  insufficient: boolean = n < N_MIN,
): Record<string, number | boolean | null | [number, number]> {
  const ok = value !== null && value !== undefined && Number.isFinite(value)
  return {
    [key]: ok ? value : null,
    [`${key}_n`]: n,
    [`${key}_ins`]: insufficient,
    [`${key}_err`]: ok && ci ? [Math.max(0, value - ci[0]), Math.max(0, ci[1] - value)] : null,
  }
}

interface GrupedProps {
  titulo: string
  unidad: string
  filas: Fila[]
  series: Serie[]
  conError?: boolean
  decimales?: 1 | 2
}

/** Barras agrupadas con n junto a cada barra, aviso y opacidad por n < 30, y nulos como "–". */
export function BarrasAgrupadas({ titulo, unidad, filas, series, conError = false, decimales = 1 }: GrupedProps) {
  const f = decimales === 2 ? fmt2 : fmt1
  return (
    <figure className="rounded-lg bg-slate-800 p-3">
      <figcaption className="mb-2 text-sm font-medium text-slate-100">
        {titulo} <span className="text-slate-300">({unidad})</span>
      </figcaption>
      <div style={{ width: '100%', height: 220 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={filas} margin={{ top: 20, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fill: TEXTO, fontSize: 12 }} stroke="#94a3b8" />
            <YAxis tick={{ fill: TEXTO, fontSize: 12 }} stroke="#94a3b8" />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: '1px solid #475569', color: '#f1f5f9' }}
              labelStyle={{ color: '#f1f5f9' }}
              itemStyle={{ color: '#f1f5f9' }}
            />
            {series.map((s) => (
              <Bar key={s.key} dataKey={s.key} name={s.name} fill={s.color} isAnimationActive={false}>
                {filas.map((fila, i) => (
                  <Cell key={i} fill={s.color} fillOpacity={fila[`${s.key}_ins`] ? OPACIDAD_INSUFICIENTE : 1} />
                ))}
                {conError && <ErrorBar dataKey={`${s.key}_err`} stroke="#f1f5f9" strokeWidth={1.5} />}
                <LabelList
                  dataKey={`${s.key}_n`}
                  position="top"
                  fill={TEXTO}
                  fontSize={11}
                  formatter={(n: unknown) => `n=${n}`}
                />
              </Bar>
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
      <ul className="mt-2 space-y-0.5 text-xs text-slate-300">
        {filas.flatMap((fila) =>
          series.map((s) => {
            const v = fila[s.key] as number | null
            return (
              <li key={`${fila.name}-${s.key}`}>
                {fila.name} · {s.name}: {v === null ? DASH : f(v)} · n={String(fila[`${s.key}_n`])}
                {fila[`${s.key}_ins`] && (
                  <span className="ml-2 rounded bg-slate-700 px-1.5 py-0.5 text-slate-100">{AVISO_MUESTRA}</span>
                )}
              </li>
            )
          }),
        )}
      </ul>
    </figure>
  )
}

const PA = '#38bdf8'
const TRAD = '#fbbf24'

export default function ComparisonCharts({ data }: { data: RecommendResponse }) {
  if (data.subset_n === 0) return null
  const { play_action: pa, blitz: bz } = data
  const sP = [{ key: 'v', name: 'Éxito', color: PA }]
  const filasEx: Fila[] = [
    { name: 'Play Action', ...campos('v', pa.play_action.success_rate, pa.play_action.n, pa.play_action.ci, pa.play_action.insufficient) },
    { name: 'Tradicional', ...campos('v', pa.traditional.success_rate, pa.traditional.n, pa.traditional.ci, pa.traditional.insufficient) },
  ]
  const filasYd: Fila[] = [
    { name: 'Play Action', ...campos('v', pa.play_action.mean_yards, pa.play_action.n, null, pa.play_action.insufficient) },
    { name: 'Tradicional', ...campos('v', pa.traditional.mean_yards, pa.traditional.n, null, pa.traditional.insufficient) },
  ]
  const filasBEx: Fila[] = [
    { name: 'Blitz', ...campos('v', bz.blitz.success_rate, bz.blitz.n, bz.blitz.ci, bz.blitz.insufficient) },
    { name: 'No Blitz', ...campos('v', bz.standard.success_rate, bz.standard.n, bz.standard.ci, bz.standard.insufficient) },
  ]
  const filasBPr: Fila[] = [
    { name: 'Blitz', ...campos('v', bz.blitz.any_pressure_pct, bz.blitz.n, null, bz.blitz.insufficient) },
    { name: 'No Blitz', ...campos('v', bz.standard.any_pressure_pct, bz.standard.n, null, bz.standard.insufficient) },
  ]
  return (
    <div className="space-y-4">
      <h3 className="text-base font-semibold text-slate-100">Play Action contra Tradicional</h3>
      <div className="grid gap-3 md:grid-cols-2">
        <BarrasAgrupadas titulo="Tasa de éxito" unidad="%, con IC de Wilson" filas={filasEx} series={sP} conError />
        <BarrasAgrupadas titulo="Yardas medias (prePenaltyPlayResult)" unidad="yardas" filas={filasYd} series={sP} decimales={2} />
      </div>
      <h3 className="text-base font-semibold text-slate-100">Blitz contra No Blitz</h3>
      <div className="grid gap-3 md:grid-cols-2">
        <BarrasAgrupadas titulo="Tasa de éxito" unidad="%, con IC de Wilson" filas={filasBEx} series={sP} conError />
        <BarrasAgrupadas titulo="Presión (any_pressure)" unidad="% de jugadas" filas={filasBPr} series={sP} />
      </div>
    </div>
  )
}
