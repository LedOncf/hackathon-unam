import { useCallback, useEffect, useRef, useState } from 'react'
import type { Focus, FiltersResponse, RecommendResponse, SamplePlayResponse } from './api/types'
import { useRequest } from './hooks/useRequest'
import { apiUrl, INITIAL_SITUATION, type Situation } from './state/situation'
import { SCENARIOS, type ScenarioId, type ScenarioPreset } from './state/scenarios'
import FilterPanel from './components/FilterPanel'
import ScenarioBar from './components/ScenarioBar'
import PanelState from './components/PanelState'
import VerdictCard from './components/VerdictCard'
import ComparisonCharts from './components/ComparisonCharts'
import PhysicsChart from './components/PhysicsChart'
import ScopeFooter from './components/ScopeFooter'
import ScenarioCard from './components/ScenarioCard'
import CoachBoard from './components/CoachBoard'

const MAX_EXCLUDE = 100

export default function App() {
  const [situation, setSituation] = useState<Situation>(INITIAL_SITUATION)
  const [activeScenario, setActiveScenario] = useState<ScenarioId | null>(null)
  // Valores vigentes para que "Reintentar" y "Cargar otra" usen siempre el estado actual.
  const situationRef = useRef<Situation>(INITIAL_SITUATION)
  const focusRef = useRef<Focus | undefined>(undefined)
  const excludeRef = useRef<string[]>([])

  const recommendUrl = useCallback(() => apiUrl('recommend', situationRef.current), [])
  const sampleUrl = useCallback(
    () =>
      apiUrl('sample-play', situationRef.current, {
        exclude: excludeRef.current.join(','),
        focus: focusRef.current,
      }),
    [],
  )

  const filters = useRequest<FiltersResponse>(() => apiUrl('filters'))
  const recommend = useRequest<RecommendResponse>(recommendUrl)
  const samplePlay = useRequest<SamplePlayResponse>(sampleUrl)

  const { run: runFilters } = filters
  const { run: runRecommend } = recommend
  const { run: runSample } = samplePlay

  const refresh = useCallback(() => {
    runRecommend(recommendUrl())
    runSample(sampleUrl())
  }, [runRecommend, runSample, recommendUrl, sampleUrl])

  // Carga inicial.
  useEffect(() => {
    runFilters(apiUrl('filters'))
    refresh()
  }, [runFilters, refresh])

  // Registra cada jugada mostrada en `exclude` (últimas 100).
  const playId = samplePlay.data?.play.id
  useEffect(() => {
    if (!playId || excludeRef.current.includes(playId)) return
    excludeRef.current = [...excludeRef.current, playId].slice(-MAX_EXCLUDE)
  }, [playId])

  // Cambio manual de selector: cierra la tarjeta, quita focus y vacía exclude.
  const handleChange = (next: Situation) => {
    situationRef.current = next
    focusRef.current = undefined
    excludeRef.current = []
    setSituation(next)
    setActiveScenario(null)
    refresh()
  }

  const handleReset = () => handleChange(INITIAL_SITUATION)

  const handleScenario = (p: ScenarioPreset) => {
    situationRef.current = p.filtro
    focusRef.current = p.focus
    excludeRef.current = []
    setSituation(p.filtro)
    setActiveScenario(p.id)
    refresh()
  }

  const handleLoadAnother = () => runSample(sampleUrl())

  const rec = recommend.data
  const preset = SCENARIOS.find((s) => s.id === activeScenario)
  const sampleLoading = samplePlay.status === 'loading'

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <header className="border-b border-slate-700 px-6 py-3">
        <h1 className="text-xl font-bold">Simulador táctico del coach NFL</h1>
      </header>
      <main className="grid gap-4 p-4 lg:grid-cols-[18rem_minmax(0,1fr)_minmax(0,1.2fr)]">
        <aside className="flex flex-col gap-6" aria-label="Panel izquierdo">
          <ScenarioBar active={activeScenario} onSelect={handleScenario} />
          <PanelState
            loading={filters.status === 'loading'}
            error={filters.error}
            onRetry={filters.retry}
          >
            <FilterPanel
              situation={situation}
              filters={filters.data}
              onChange={handleChange}
              onReset={handleReset}
            />
          </PanelState>
        </aside>

        <section className="flex flex-col gap-4" aria-label="Panel central">
          <PanelState
            loading={recommend.status === 'loading'}
            error={recommend.error}
            onRetry={recommend.retry}
            empty={rec?.subset_n === 0}
          >
            {rec && (
              <div className="space-y-4">
                {preset && recommend.status === 'ok' && (
                  <ScenarioCard
                    scenarioId={preset.id}
                    titulo={preset.texto}
                    data={rec}
                    preferred={samplePlay.data?.preferred ?? null}
                    onClose={() => setActiveScenario(null)}
                  />
                )}
                <VerdictCard data={rec} />
                <ComparisonCharts data={rec} />
                <PhysicsChart data={rec} />
              </div>
            )}
          </PanelState>
          <ScopeFooter />
        </section>

        <section className="flex flex-col gap-3" aria-label="Panel derecho">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-base font-semibold">Pizarra de tracking</h2>
            <button
              type="button"
              onClick={handleLoadAnother}
              disabled={sampleLoading}
              className="rounded bg-sky-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-sky-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Cargar otra jugada real
            </button>
          </div>
          <PanelState loading={sampleLoading} error={samplePlay.error} onRetry={samplePlay.retry}>
            <CoachBoard play={samplePlay.data} />
          </PanelState>
        </section>
      </main>
    </div>
  )
}
