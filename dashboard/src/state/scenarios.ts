import type { Focus } from '../api/types'
import type { Situation } from './situation'

export type ScenarioId = 'play_action_cover2_caja7' | 'trampa_red_zone' | 'blitz_empty'

export interface ScenarioPreset {
  id: ScenarioId
  texto: string
  filtro: Situation
  focus: Focus
}

// Solo filtros y focus; ninguna cifra de resultados vive en el cliente.
export const SCENARIOS: readonly ScenarioPreset[] = [
  {
    id: 'play_action_cover2_caja7',
    texto: 'Play Action vs Cover-2 (Caja de 7)',
    filtro: { down: '', ytg: '', coverage: 'Cover-2', formation: '', box: '7' },
    focus: 'bite',
  },
  {
    id: 'trampa_red_zone',
    texto: 'La Trampa de Red Zone',
    filtro: { down: '', ytg: '', coverage: 'Red Zone', formation: '', box: '' },
    focus: 'pa_fallida',
  },
  {
    id: 'blitz_empty',
    texto: 'Blitz vs Formación Empty',
    filtro: { down: '', ytg: '', coverage: '', formation: 'EMPTY', box: '' },
    focus: 'blitz_exitoso',
  },
]
