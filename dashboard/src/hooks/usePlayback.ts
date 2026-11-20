import { useCallback, useEffect, useState } from 'react'

export const PLAYBACK_INTERVAL_MS = 100

export interface PlaybackSource {
  /** Identidad de la jugada: al cambiar se detiene y se vuelve a `snap`. */
  id: string
  snap: number
  last: number
}

export interface Playback {
  frame: number
  playing: boolean
  snap: number
  last: number
  /** Solo hay un frame entre ball_snap y pass_forward (17.24). */
  single: boolean
  toggle: () => void
  seek: (frame: number) => void
  goToEnd: () => void
}

/** Playback_Controller (17): avanza 1 frame cada 100 ms entre `snap` y `last`. */
export function usePlayback(source: PlaybackSource | null): Playback {
  const id = source?.id ?? null
  const snap = source?.snap ?? 0
  const last = source ? Math.max(source.last, source.snap) : 0

  const [frame, setFrame] = useState(snap)
  const [playing, setPlaying] = useState(false)

  // Jugada nueva: pausa y vuelta al snap (17.3, 17.10).
  useEffect(() => {
    setPlaying(false)
    setFrame(snap)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  useEffect(() => {
    if (!playing) return
    const timer = setInterval(() => {
      setFrame((f) => (f < last ? f + 1 : f))
    }, PLAYBACK_INTERVAL_MS)
    return () => clearInterval(timer)
  }, [playing, id, last])

  // Al llegar a pass_forward la animación se detiene (17.5).
  useEffect(() => {
    if (playing && frame >= last) setPlaying(false)
  }, [playing, frame, last])

  const clamp = useCallback((f: number) => Math.min(Math.max(f, snap), last), [snap, last])

  const toggle = useCallback(() => {
    if (last <= snap) return
    if (playing) {
      setPlaying(false)
      return
    }
    if (frame >= last) setFrame(snap) // 17.6
    setPlaying(true)
  }, [playing, frame, snap, last])

  const seek = useCallback(
    (f: number) => {
      setPlaying(false)
      setFrame(clamp(f))
    },
    [clamp],
  )

  const goToEnd = useCallback(() => {
    setPlaying(false)
    setFrame(last)
  }, [last])

  return { frame: clamp(frame), playing, snap, last, single: last <= snap, toggle, seek, goToEnd }
}
