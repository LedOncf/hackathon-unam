import type { ReactNode } from 'react'

export interface PanelStateProps {
  loading: boolean
  error: string | null
  onRetry: () => void
  /** Subset vacío (subset_n = 0): se oculta el contenido y se muestra el mensaje. */
  empty?: boolean
  children: ReactNode
}

export const MENSAJE_VACIO = 'No hay jugadas para la situación elegida.'

/** Indicador de carga y error con "Reintentar". Conserva el contenido previo. */
export default function PanelState({ loading, error, onRetry, empty = false, children }: PanelStateProps) {
  return (
    <div className="relative" aria-busy={loading}>
      {loading && (
        <p role="status" className="mb-2 rounded bg-slate-800 px-3 py-1 text-sm text-slate-100">
          Cargando…
        </p>
      )}
      {error && !loading && (
        <div role="alert" className="mb-2 flex items-center justify-between gap-3 rounded border border-red-400 bg-red-950 px-3 py-2 text-sm text-red-100">
          <span>{error}</span>
          <button
            type="button"
            onClick={onRetry}
            className="rounded bg-red-200 px-3 py-1 font-medium text-slate-900 hover:bg-red-100"
          >
            Reintentar
          </button>
        </div>
      )}
      {empty ? (
        <p className="rounded bg-slate-800 px-4 py-6 text-center text-slate-100">{MENSAJE_VACIO}</p>
      ) : (
        children
      )}
    </div>
  )
}
