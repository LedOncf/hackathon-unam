import { useMemo } from 'react'
import type { PlayerTrack, SamplePlayResponse } from '../api/types'
import { viewWindow, type BoardPlayer } from '../lib/board'
import { fmt1 } from '../lib/format'
import { usePlayback } from '../hooks/usePlayback'
import FieldSvg from './FieldSvg'
import PlayerMarker from './PlayerMarker'
import Legend from './Legend'
import PlayMeta from './PlayMeta'
import PlaybackController from './PlaybackController'
import LiveMetrics from './LiveMetrics'

type Pt = { x: number; y: number }

function indexTrack(p: PlayerTrack): Map<number, Pt> {
  const m = new Map<number, Pt>()
  for (const t of p.track) m.set(t.frameId, { x: t.x_norm, y: t.y_norm })
  return m
}

/**
 * Pizarra: cancha, trayectorias, flechas de LB, línea QB–Rush, marcadores,
 * leyenda, metadatos y reproducción. Con `error` conserva la última jugada (13.10).
 */
export default function CoachBoard({
  play,
  error,
}: {
  play: SamplePlayResponse | null
  error?: string | null
}) {
  const snap = play?.snap_frame ?? 0
  const last = play?.pass_forward_frame ?? 0
  const playback = usePlayback(play ? { id: play.play.id, snap, last } : null)

  const data = useMemo(() => {
    if (!play) return null
    const inRange = (f: number) => f >= play.snap_frame && f <= play.pass_forward_frame
    const players = play.players.map((p) => ({
      p,
      pts: indexTrack(p),
      path: p.track.filter((t) => inRange(t.frameId)),
    }))
    const board: BoardPlayer[] = players.map(({ p, path }) => ({
      role: p.role,
      is_lb: p.is_lb,
      track: path,
    }))
    const ball = play.ball.filter((b) => inRange(b.frameId))
    const win = viewWindow(board, ball, 3)
    const ballPts = new Map<number, Pt>(ball.map((b) => [b.frameId, { x: b.x_norm, y: b.y_norm }]))
    // QB y Pass Rush más cercano en pass_forward (13.5)
    const qb = players.find((e) => e.p.role === 'QB')?.pts.get(play.pass_forward_frame)
    let rush: Pt | null = null
    if (qb) {
      let best = Infinity
      for (const e of players) {
        if (e.p.role !== 'Pass Rush') continue
        const r = e.pts.get(play.pass_forward_frame)
        if (!r) continue
        const d = Math.hypot(r.x - qb.x, r.y - qb.y)
        if (d < best) {
          best = d
          rush = r
        }
      }
    }
    return { players, win, ballPts, qb, rush }
  }, [play])

  return (
    <section className="space-y-3" aria-label="Pizarra de tracking" data-testid="coach-board">
      {error && (
        <p role="alert" className="rounded border border-red-500 bg-red-950 p-2 text-sm text-red-100">
          {error}
        </p>
      )}
      {!play || !data ? (
        !error && <p className="text-sm text-slate-300">Sin jugada para mostrar.</p>
      ) : (
        <>
          <FieldSvg window={data.win}>
            <defs>
              <marker id="lb-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
                <path d="M0,0 L10,5 L0,10 z" fill="#e879f9" />
              </marker>
            </defs>
            {data.players.map(({ p, path }) => (
              <polyline
                key={`t${p.nflId}`}
                points={path.map((t) => `${t.x_norm},${t.y_norm}`).join(' ')}
                fill="none"
                stroke="#e2e8f0"
                strokeOpacity={0.3}
                strokeWidth={0.2}
              />
            ))}
            {data.players
              .filter(({ p }) => p.is_lb)
              .map(({ p, pts }) => {
                const a = pts.get(play.snap_frame)
                const b = pts.get(play.pass_forward_frame)
                if (!a || !b) return null
                return (
                  <g key={`lb${p.nflId}`}>
                    <line
                      x1={a.x}
                      y1={a.y}
                      x2={b.x}
                      y2={b.y}
                      stroke="#e879f9"
                      strokeWidth={0.4}
                      markerEnd="url(#lb-arrow)"
                      data-testid="lb-arrow"
                    />
                    <text
                      x={(a.x + b.x) / 2}
                      y={(a.y + b.y) / 2 + 2.2}
                      fontSize={1.3}
                      textAnchor="middle"
                      fill="#f5d0fe"
                      stroke="#0f172a"
                      strokeWidth={0.1}
                      paintOrder="stroke"
                    >
                      {play.play.lb_bite_yards === null ? '–' : `${fmt1(play.play.lb_bite_yards)} yd`}
                    </text>
                  </g>
                )
              })}
            {data.qb && data.rush && (
              <g data-testid="qb-rush-line">
                <line
                  x1={data.qb.x}
                  y1={data.qb.y}
                  x2={data.rush.x}
                  y2={data.rush.y}
                  stroke="#ef4444"
                  strokeWidth={0.3}
                  strokeDasharray="0.8 0.5"
                />
                <text
                  x={(data.qb.x + data.rush.x) / 2}
                  y={(data.qb.y + data.rush.y) / 2 - 0.6}
                  fontSize={1.3}
                  textAnchor="middle"
                  fill="#fecaca"
                  stroke="#0f172a"
                  strokeWidth={0.1}
                  paintOrder="stroke"
                >
                  {play.play.min_rusher_dist_at_throw === null
                    ? '–'
                    : `${fmt1(play.play.min_rusher_dist_at_throw)} yd`}
                </text>
              </g>
            )}
            {data.ballPts.get(playback.frame) && (
              <ellipse
                cx={data.ballPts.get(playback.frame)!.x}
                cy={data.ballPts.get(playback.frame)!.y}
                rx={0.6}
                ry={0.4}
                fill="#92400e"
                stroke="#f8fafc"
                strokeWidth={0.12}
              />
            )}
            {data.players.map(({ p, pts }) => {
              const pt = pts.get(playback.frame)
              if (!pt) return null
              return <PlayerMarker key={p.nflId} role={p.role} label={p.label} x={pt.x} y={pt.y} />
            })}
          </FieldSvg>
          <Legend />
          <PlaybackController playback={playback} />
          <LiveMetrics play={play} frame={playback.frame} />
          <PlayMeta play={play.play} />
          <p className="text-xs text-slate-300">
            Jugada real de ejemplo: ilustra, no prueba, la tendencia
          </p>
        </>
      )}
    </section>
  )
}
