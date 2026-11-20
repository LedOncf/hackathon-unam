import type { RecommendResponse, VerdictCode } from '../api/types'
import { dash, signed1 } from '../lib/format'

const ESTILO: Record<VerdictCode, string> = {
  LLAMAR_PLAY_ACTION: 'border-emerald-400 bg-emerald-900 text-emerald-50',
  EVITAR_PLAY_ACTION: 'border-red-400 bg-red-900 text-red-50',
  SIN_VENTAJA_CLARA: 'border-amber-400 bg-amber-900 text-amber-50',
  MUESTRA_INSUFICIENTE: 'border-slate-400 bg-slate-700 text-slate-50',
}

export default function VerdictCard({ data }: { data: RecommendResponse }) {
  if (data.subset_n === 0) return null
  const v = data.verdict
  const ci = v.effect_pp_ci
  return (
    <section
      data-verdict={v.code}
      aria-label="Veredicto"
      className={`rounded-lg border-2 p-4 ${ESTILO[v.code]}`}
    >
      <p className="text-xl font-semibold">{v.text}</p>
      <p className="mt-2 text-sm">
        Efecto: <strong>{signed1(v.effect_pp)} pp</strong>
        {' · '}IC 95 %: límite inferior {ci ? signed1(ci[0]) : dash(null)} pp, límite superior{' '}
        {ci ? signed1(ci[1]) : dash(null)} pp
      </p>
      <p className="mt-1 text-xs">Jugadas en la situación: {data.subset_n}</p>
    </section>
  )
}
