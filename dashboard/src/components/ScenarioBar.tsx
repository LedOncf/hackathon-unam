import { SCENARIOS, type ScenarioId, type ScenarioPreset } from '../state/scenarios'

interface Props {
  active: ScenarioId | null
  onSelect: (preset: ScenarioPreset) => void
}

export default function ScenarioBar({ active, onSelect }: Props) {
  return (
    <section aria-label="Escenarios tácticos rápidos" className="flex flex-col gap-2">
      <h2 className="text-base font-semibold text-slate-100">Escenarios rápidos</h2>
      {SCENARIOS.map((s) => {
        const pressed = active === s.id
        return (
          <button
            key={s.id}
            type="button"
            aria-pressed={pressed}
            onClick={() => onSelect(s)}
            className={
              'rounded border px-3 py-2 text-left text-sm ' +
              (pressed
                ? 'border-sky-400 bg-sky-800 text-white'
                : 'border-slate-500 bg-slate-800 text-slate-100 hover:bg-slate-700')
            }
          >
            {s.texto}
          </button>
        )
      })}
    </section>
  )
}
