import type { RecommendResponse } from '../api/types'
import { BarrasAgrupadas, campos, type Fila, type Serie } from './ComparisonCharts'

const pctOrNull = (v: number | null): number | null => (v === null ? null : v * 100)

export default function PhysicsChart({ data }: { data: RecommendResponse }) {
  if (data.subset_n === 0) return null
  const { lb_bite_table, protection_table } = data.physics
  const seriesLb: Serie[] = [
    { key: 'pa', name: 'Play Action', color: '#38bdf8' },
    { key: 'trad', name: 'Tradicional', color: '#fbbf24' },
  ]
  const filasLb: Fila[] = lb_bite_table.map((r) => ({
    name: `${r.range} yd`,
    ...campos('pa', pctOrNull(r.pa_success_rate), r.n_pa),
    ...campos('trad', pctOrNull(r.trad_success_rate), r.n_trad),
  }))
  const filasLbPr: Fila[] = lb_bite_table.map((r) => ({
    name: `${r.range} yd`,
    ...campos('pa', pctOrNull(r.pa_pressure_rate), r.n_pa),
    ...campos('trad', pctOrNull(r.trad_pressure_rate), r.n_trad),
  }))
  const seriesPr: Serie[] = [
    { key: 'ex', name: 'Éxito', color: '#34d399' },
    { key: 'pr', name: 'Presión', color: '#f87171' },
  ]
  const filasPr: Fila[] = protection_table.map((r) => ({
    name: r.category,
    ...campos('ex', pctOrNull(r.success_rate), r.n, null, r.insufficient),
    ...campos('pr', pctOrNull(r.any_pressure), r.n, null, r.insufficient),
  }))
  return (
    <div className="space-y-4">
      <h3 className="text-base font-semibold text-slate-100">Física del Tracking</h3>
      <div className="grid gap-3 md:grid-cols-2">
        <BarrasAgrupadas titulo="Éxito por rango de lb_bite_yards" unidad="%" filas={filasLb} series={seriesLb} />
        <BarrasAgrupadas titulo="Presión por rango de lb_bite_yards" unidad="%" filas={filasLbPr} series={seriesLb} />
        <BarrasAgrupadas titulo="Éxito y presión por protección (protection_advantage)" unidad="%" filas={filasPr} series={seriesPr} />
      </div>
    </div>
  )
}
