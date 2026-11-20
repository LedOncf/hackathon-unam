import type { ReactNode } from 'react'
import { fieldYardNumber, type ViewWindow } from '../lib/board'

const FIELD_WIDTH = 53.3
const FIELD_LENGTH = 120

/** Cancha NFL en yardas: líneas cada 5 yardas y números cada 10 (13.1). */
export default function FieldSvg({
  window: win,
  children,
}: {
  window: ViewWindow
  children?: ReactNode
}) {
  const w = win.x1 - win.x0
  const h = win.y1 - win.y0
  // La ventana puede rebasar la cancha: el césped se recorta a 0–120 × 0–53.3.
  const gx0 = Math.max(win.x0, 0)
  const gx1 = Math.min(win.x1, FIELD_LENGTH)
  const gy0 = Math.max(win.y0, 0)
  const gy1 = Math.min(win.y1, FIELD_WIDTH)
  const hasGrass = gx1 > gx0 && gy1 > gy0

  const lines: number[] = []
  for (let x = Math.ceil(gx0 / 5) * 5; x <= gx1; x += 5) lines.push(x)

  const numTop = gy0 + 2.8
  const numBottom = gy1 - 1
  const numbers = lines.filter((x) => fieldYardNumber(x) !== null)

  return (
    <svg
      viewBox={`${win.x0} ${win.y0} ${w} ${h}`}
      preserveAspectRatio="xMidYMid meet"
      className="h-auto w-full rounded border border-slate-700 bg-slate-950"
      role="img"
      aria-label="Pizarra de la jugada sobre una cancha NFL"
      data-testid="field-svg"
    >
      {hasGrass && (
        <rect x={gx0} y={gy0} width={gx1 - gx0} height={gy1 - gy0} fill="#14532d" />
      )}
      {lines.map((x) => (
        <line
          key={x}
          x1={x}
          x2={x}
          y1={gy0}
          y2={gy1}
          stroke="#e2e8f0"
          strokeOpacity={x % 10 === 0 ? 0.45 : 0.25}
          strokeWidth={0.15}
        />
      ))}
      {numbers.map((x) => (
        <g key={`n${x}`} fill="#e2e8f0" fillOpacity={0.55} fontSize={2.4} textAnchor="middle">
          <text x={x} y={numTop}>{fieldYardNumber(x)}</text>
          <text x={x} y={numBottom}>{fieldYardNumber(x)}</text>
        </g>
      ))}
      {win.y0 <= 0 && <line x1={gx0} x2={gx1} y1={0} y2={0} stroke="#e2e8f0" strokeWidth={0.3} />}
      {win.y1 >= FIELD_WIDTH && (
        <line x1={gx0} x2={gx1} y1={FIELD_WIDTH} y2={FIELD_WIDTH} stroke="#e2e8f0" strokeWidth={0.3} />
      )}
      {children}
    </svg>
  )
}
