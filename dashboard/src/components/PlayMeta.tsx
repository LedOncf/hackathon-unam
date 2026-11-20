import type { PlayMeta as PlayMetaData } from '../api/types'

const NA = 'No disponible'
const text = (v: string | number | null | undefined) =>
  v === null || v === undefined || v === '' ? NA : String(v)
const yesNo = (v: number | null | undefined) =>
  v === null || v === undefined ? NA : v ? 'Sí' : 'No'

/** Metadatos de la jugada; los ausentes dicen "No disponible" (13.7). */
export default function PlayMeta({ play }: { play: PlayMetaData }) {
  const rows: [string, string][] = [
    ['Equipo ofensivo', text(play.offense)],
    ['Equipo defensivo', text(play.defense)],
    ['Semana', text(play.week)],
    ['Down', text(play.down)],
    ['Yardas por recorrer', text(play.yards_to_go)],
    ['Cobertura', text(play.coverage)],
    ['Formación', text(play.formation)],
    ['Play Action', yesNo(play.play_action)],
    ['Blitz', yesNo(play.is_blitz)],
    ['Jugada exitosa', yesNo(play.is_success)],
  ]
  return (
    <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm sm:grid-cols-3" data-testid="play-meta">
      {rows.map(([k, v]) => (
        <div key={k}>
          <dt className="text-slate-400">{k}</dt>
          <dd className="font-medium">{v}</dd>
        </div>
      ))}
    </dl>
  )
}
