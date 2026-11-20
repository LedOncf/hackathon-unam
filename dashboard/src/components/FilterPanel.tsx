import type { FiltersResponse } from '../api/types'
import type { Situation } from '../state/situation'

interface Props {
  situation: Situation
  filters: FiltersResponse | null
  onChange: (next: Situation) => void
  onReset: () => void
}

interface Opt { value: string; label: string }

const TODOS: Opt = { value: '', label: 'Todos' }

const DOWN_OPTS: Opt[] = [TODOS, { value: '1', label: '1' }, { value: '2', label: '2' }, { value: '3-4', label: '3-4' }]
const YTG_OPTS: Opt[] = [
  TODOS,
  { value: 'corta', label: 'corta' },
  { value: 'media', label: 'media' },
  { value: 'larga', label: 'larga' },
]

/** Valores únicos ordenados alfabéticamente. */
function textOpts(values: string[] | undefined): Opt[] {
  const uniq = Array.from(new Set(values ?? [])).sort((a, b) => a.localeCompare(b, 'es'))
  return [TODOS, ...uniq.map((v) => ({ value: v, label: v }))]
}

/** Siempre incluye 5, 6, 7 y 8; sin duplicados; orden numérico ascendente. */
export function boxOpts(values: number[] | undefined): Opt[] {
  const uniq = Array.from(new Set([5, 6, 7, 8, ...(values ?? [])])).sort((a, b) => a - b)
  return [TODOS, ...uniq.map((v) => ({ value: String(v), label: String(v) }))]
}

interface SelectProps {
  id: string
  label: string
  value: string
  options: Opt[]
  onChange: (v: string) => void
}

function Select({ id, label, value, options, onChange }: SelectProps) {
  // Si el valor vigente (p. ej. de un escenario) no está en la lista, se conserva visible.
  const opts = options.some((o) => o.value === value) ? options : [...options, { value, label: value }]
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-sm font-medium text-slate-200">
        {label}
      </label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded border border-slate-600 bg-slate-800 px-2 py-1.5 text-sm text-slate-100"
      >
        {opts.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  )
}

export default function FilterPanel({ situation, filters, onChange, onReset }: Props) {
  const set = (patch: Partial<Situation>) => onChange({ ...situation, ...patch })
  return (
    <section aria-label="Situación de juego" className="flex flex-col gap-3">
      <h2 className="text-base font-semibold text-slate-100">Situación de juego</h2>
      <Select id="f-down" label="Down" value={situation.down} options={DOWN_OPTS} onChange={(v) => set({ down: v })} />
      <Select
        id="f-ytg"
        label="Yardas por Recorrer"
        value={situation.ytg}
        options={YTG_OPTS}
        onChange={(v) => set({ ytg: v })}
      />
      <Select
        id="f-coverage"
        label="Cobertura"
        value={situation.coverage}
        options={textOpts(filters?.pff_passCoverage)}
        onChange={(v) => set({ coverage: v })}
      />
      <Select
        id="f-formation"
        label="Formación"
        value={situation.formation}
        options={textOpts(filters?.offenseFormation)}
        onChange={(v) => set({ formation: v })}
      />
      <Select
        id="f-box"
        label="Defensores en la Caja"
        value={situation.box}
        options={boxOpts(filters?.defendersInBox)}
        onChange={(v) => set({ box: v })}
      />
      <button
        type="button"
        onClick={onReset}
        className="rounded border border-slate-500 px-3 py-1.5 text-sm text-slate-100 hover:bg-slate-700"
      >
        Restablecer
      </button>
    </section>
  )
}
