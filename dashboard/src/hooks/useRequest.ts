import { useCallback, useEffect, useRef, useState } from 'react'
import { ApiError, getJson } from '../api/client'

export type RequestStatus = 'idle' | 'loading' | 'ok' | 'error'

export interface RequestState<T> {
  status: RequestStatus
  /** Último dato recibido con éxito; se conserva durante loading y error. */
  data: T | null
  error: string | null
}

/**
 * Solicitud con cancelación y descarte de respuestas obsoletas.
 * `getUrl` se evalúa en cada retry() para usar la situación vigente.
 */
export function useRequest<T>(getUrl?: () => string | null) {
  const [state, setState] = useState<RequestState<T>>({ status: 'idle', data: null, error: null })
  const requestId = useRef(0)
  const ctrlRef = useRef<AbortController | null>(null)
  const getUrlRef = useRef(getUrl)
  getUrlRef.current = getUrl

  const run = useCallback((url: string) => {
    const id = ++requestId.current
    ctrlRef.current?.abort()
    const ctrl = new AbortController()
    ctrlRef.current = ctrl
    setState((s) => ({ status: 'loading', data: s.data, error: null }))
    getJson<T>(url, ctrl.signal)
      .then((data) => {
        if (id !== requestId.current) return
        setState({ status: 'ok', data, error: null })
      })
      .catch((e: unknown) => {
        if (id !== requestId.current) return
        if (e instanceof ApiError && e.kind === 'abort') return
        const message = e instanceof ApiError ? e.message : 'Error inesperado.'
        setState((s) => ({ status: 'error', data: s.data, error: message }))
      })
  }, [])

  const retry = useCallback(() => {
    const url = getUrlRef.current?.()
    if (url) run(url)
  }, [run])

  useEffect(() => () => {
    requestId.current++
    ctrlRef.current?.abort()
  }, [])

  return { ...state, run, retry }
}
