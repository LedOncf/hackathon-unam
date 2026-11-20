import type { ReactNode } from 'react'
import type { Pair, RecommendResponse } from '../api/types'
import { dash, fmt2, pct, signed1 } from '../lib/format'
import type { ScenarioId } from '../state/scenarios'

export interface ScenarioCardProps {
  scenarioId: ScenarioId
  titulo: string
  data: RecommendResponse
  /** `preferred` de /api/sample-play; null si aún no hay jugada. */
  preferred: boolean | null
  onClose: () => void
}

const INSUFICIENTE = 'Muestra insuficiente (n < 30)'
const SIN_PATRON = 'Jugada de ejemplo sin el patrón destacado'
const PIE = 'Éxito medido por down y distancia; sin EPA. Una sola jugada ilustra, no prueba.'

const ciContieneCero = (ci: Pair): boolean => ci !== null && ci[0] <= 0 && 0 <= ci[1]
const ciTexto = (ci: Pair): string => (ci ? `[${signed1(ci[0])}, ${signed1(ci[1])}] pp` : dash(null))

function Tag({ children }: { children: ReactNode }) {
  return (
    <span className="ml-2 rounded bg-slate-700 px-1.5 py-0.5 text-xs text-slate-100">{children}</span>
  )
}

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex flex-wrap items-baseline justify-between gap-2 text-sm">
      <span className="text-slate-300">{label}</span>
      <span className="text-slate-100">{children}</span>
    </div>
  )
}

function Diff({ label, effect, ci }: { label: string; effect: number | null; ci: Pair }) {
  return (
    <Row label={label}>
      {signed1(effect)} pp, IC 95 % {ciTexto(ci)}
      {ciContieneCero(ci) && <Tag>no concluyente</Tag>}
    </Row>
  )
}

function Grupo({ nombre, n, insufficient }: { nombre: string; n: number; insufficient: boolean }) {
  return (
    <Row label={`n de ${nombre}`}>
      {n}
      {insufficient && <Tag>{INSUFICIENTE}</Tag>}
    </Row>
  )
}

export default function ScenarioCard({ scenarioId, titulo, data, preferred, onClose }: ScenarioCardProps) {
  const pa = data.play_action
  const bl = data.blitz

  let cuerpo: ReactNode
  if (scenarioId === 'play_action_cover2_caja7') {
    cuerpo = (
      <>
        <p className="text-sm text-slate-300">Caja de 7: la cifra aplica solo a jugadas con 7 defensores en la caja.</p>
        <Diff label="Diferencia de éxito (Play Action frente a Tradicional)" effect={pa.effect_pp} ci={pa.effect_pp_ci} />
        <Grupo nombre="Play Action" n={pa.play_action.n} insufficient={pa.play_action.insufficient} />
        <Grupo nombre="Tradicional" n={pa.traditional.n} insufficient={pa.traditional.insufficient} />
        <Row label="Avance medio de LB, Play Action">{fmt2(pa.play_action.lb_bite.mean)} yd</Row>
        <Row label="Avance medio de LB, Tradicional">{fmt2(pa.traditional.lb_bite.mean)} yd</Row>
      </>
    )
  } else if (scenarioId === 'trampa_red_zone') {
    cuerpo = (
      <>
        <Row label="Diferencia de yardas (Play Action frente a Tradicional)">{fmt2(pa.effect_yards)} yd</Row>
        <Diff label="Diferencia de éxito" effect={pa.effect_pp} ci={pa.effect_pp_ci} />
        <Row label="Veredicto">{data.verdict.code}</Row>
        <Grupo nombre="Play Action" n={pa.play_action.n} insufficient={pa.play_action.insufficient} />
        <Grupo nombre="Tradicional" n={pa.traditional.n} insufficient={pa.traditional.insufficient} />
      </>
    )
  } else {
    cuerpo = (
      <>
        <Row label="Éxito con blitz">
          {pct(bl.blitz.success_rate)}, IC 95 % {bl.blitz.ci ? `[${pct(bl.blitz.ci[0])}, ${pct(bl.blitz.ci[1])}]` : dash(null)}
        </Row>
        <Row label="Tiempo al lanzamiento con blitz">
          {fmt2(bl.blitz.time_to_throw.mean)} s (n = {bl.blitz.time_to_throw.n_used})
        </Row>
        <Diff label="Diferencia de éxito (blitz frente a sin blitz)" effect={bl.effect_pp} ci={bl.effect_pp_ci} />
        <Grupo nombre="blitz" n={bl.blitz.n} insufficient={bl.blitz.insufficient} />
        <Grupo nombre="sin blitz" n={bl.standard.n} insufficient={bl.standard.insufficient} />
      </>
    )
  }

  return (
    <section
      aria-label="Escenario activo"
      className="space-y-2 rounded-lg border border-slate-700 bg-slate-900 p-4 text-slate-100"
    >
      <header className="flex items-start justify-between gap-2">
        <h3 className="text-base font-semibold">{titulo}</h3>
        <button
          type="button"
          onClick={onClose}
          aria-label="Cerrar escenario"
          className="rounded px-2 text-slate-300 hover:text-slate-100"
        >
          ×
        </button>
      </header>
      {cuerpo}
      {preferred === false && <p className="text-sm text-slate-100">{SIN_PATRON}</p>}
      <p className="border-t border-slate-700 pt-2 text-xs text-slate-300">{PIE}</p>
    </section>
  )
}
