import type { SamplePlayResponse } from '../api/types'
import { liveLbAdvance, liveQbRushDist } from '../lib/board'
import { fmt1 } from '../lib/format'

export default function LiveMetrics({
  play,
  frame,
}: {
  play: SamplePlayResponse
  frame: number
}) {
  const lb = liveLbAdvance(play.players, play.snap_frame, frame)
  const rush = liveQbRushDist(play.players, frame)
  const showLbRef = frame === play.snap_frame + 10
  const showRushRef = frame === play.pass_forward_frame

  return (
    <dl className="grid gap-2 text-sm sm:grid-cols-2" data-testid="live-metrics">
      <div>
        <dt className="text-slate-600">Avance de LB</dt>
        <dd className="font-semibold tabular-nums">
          {lb === null ? '–' : `${fmt1(lb)} yd`}
          {showLbRef && (
            <span className="ml-2 text-xs font-normal text-slate-600">
              Referencia lb_bite_yards (1 s tras el snap): {fmt1(play.play.lb_bite_yards)} yd
            </span>
          )}
        </dd>
      </div>
      <div>
        <dt className="text-slate-600">Distancia QB–Rush más cercano</dt>
        <dd className="font-semibold tabular-nums">
          {rush === null ? '–' : `${fmt1(rush)} yd`}
          {showRushRef && (
            <span className="ml-2 text-xs font-normal text-slate-600">
              Referencia min_rusher_dist_at_throw: {fmt1(play.play.min_rusher_dist_at_throw)} yd
            </span>
          )}
        </dd>
      </div>
    </dl>
  )
}
