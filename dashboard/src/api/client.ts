// Cliente HTTP. Las rutas son relativas (sin diagonal inicial) para funcionar desde cualquier base.
export const TIMEOUT_MS = 10_000

export type ApiErrorKind = 'network' | 'timeout' | 'http' | 'abort'

export class ApiError extends Error {
  kind: ApiErrorKind
  status: number | null
  constructor(kind: ApiErrorKind, message: string, status: number | null = null) {
    super(message)
    this.name = 'ApiError'
    this.kind = kind
    this.status = status
  }
}

export const MSG_NETWORK = 'No se pudo conectar con el servidor.'
export const MSG_TIMEOUT = 'La solicitud tardó demasiado. Intenta de nuevo.'

function httpMessage(status: number, detail: unknown): string {
  if ([404, 422, 503].includes(status) && typeof detail === 'string' && detail.trim() !== '') {
    return detail
  }
  return `Error del servidor (código ${status}).`
}

/**
 * GET con JSON. `signal` permite cancelar desde fuera (nueva solicitud o desmontaje).
 * Un abort externo lanza ApiError('abort'); el vencimiento de 10 s lanza ApiError('timeout').
 */
export async function getJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  const ctrl = new AbortController()
  let timedOut = false
  const timer = setTimeout(() => {
    timedOut = true
    ctrl.abort()
  }, TIMEOUT_MS)
  const onExternalAbort = () => ctrl.abort()
  if (signal) {
    if (signal.aborted) ctrl.abort()
    else signal.addEventListener('abort', onExternalAbort)
  }
  try {
    let res: Response
    try {
      res = await fetch(url, { signal: ctrl.signal, headers: { Accept: 'application/json' } })
    } catch {
      if (timedOut) throw new ApiError('timeout', MSG_TIMEOUT)
      if (ctrl.signal.aborted) throw new ApiError('abort', 'Solicitud cancelada.')
      throw new ApiError('network', MSG_NETWORK)
    }
    if (!res.ok) {
      let detail: unknown = null
      try {
        detail = ((await res.json()) as { detail?: unknown }).detail
      } catch {
        detail = null
      }
      throw new ApiError('http', httpMessage(res.status, detail), res.status)
    }
    try {
      return (await res.json()) as T
    } catch {
      if (timedOut) throw new ApiError('timeout', MSG_TIMEOUT)
      if (ctrl.signal.aborted) throw new ApiError('abort', 'Solicitud cancelada.')
      throw new ApiError('network', MSG_NETWORK)
    }
  } finally {
    clearTimeout(timer)
    signal?.removeEventListener('abort', onExternalAbort)
  }
}
