import type { Playback } from '../hooks/usePlayback'

export default function PlaybackController({ playback }: { playback: Playback }) {
  const { frame, playing, snap, last, single, toggle, seek, goToEnd } = playback
  const seconds = ((frame - snap) / 10).toFixed(1)

  return (
    <div className="flex flex-wrap items-center gap-3 text-sm" data-testid="playback-controller">
      <button
        type="button"
        onClick={toggle}
        disabled={single}
        className="rounded border border-slate-300 px-3 py-1 font-medium disabled:opacity-50"
      >
        {playing ? 'Pausa' : 'Reproducir'}
      </button>
      <label className="flex min-w-[12rem] flex-1 items-center gap-2">
        <input
          type="range"
          className="flex-1"
          min={snap}
          max={last}
          step={1}
          value={frame}
          disabled={single}
          onChange={(e) => seek(Number(e.target.value))}
          aria-label="Tiempo desde el snap"
        />
        <span className="whitespace-nowrap tabular-nums">Tiempo desde el snap: {seconds} s</span>
      </label>
      <button
        type="button"
        onClick={goToEnd}
        className="rounded border border-slate-300 px-3 py-1"
      >
        Ir a pass_forward
      </button>
    </div>
  )
}
