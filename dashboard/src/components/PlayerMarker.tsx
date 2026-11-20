import type { Role } from '../api/types'

export interface RoleStyle {
  shape: 'star' | 'triangle' | 'square' | 'diamond' | 'circle' | 'hexagon'
  color: string
  /** Texto de leyenda del símbolo. */
  symbol: string
}

/** Color + forma únicos por rol (13.3). */
export const ROLE_STYLES: Record<Role, RoleStyle> = {
  QB: { shape: 'star', color: '#facc15', symbol: '★' },
  'Pass Route': { shape: 'triangle', color: '#3b82f6', symbol: '▲' },
  'Pass Block': { shape: 'square', color: '#22d3ee', symbol: '■' },
  'Pass Rush': { shape: 'diamond', color: '#ef4444', symbol: '◆' },
  Coverage: { shape: 'circle', color: '#fb923c', symbol: '●' },
  LB: { shape: 'hexagon', color: '#e879f9', symbol: '⬢' },
}

/** Tamaño del Player_Label en yardas (17.18). */
export function labelSize(role: Role): number {
  return role === 'QB' || role === 'LB' || role === 'Pass Rush' ? 1.6 : 1.1
}

const R = 1

function polygon(cx: number, cy: number, n: number, r: number, rot: number): string {
  const pts: string[] = []
  for (let i = 0; i < n; i++) {
    const a = rot + (2 * Math.PI * i) / n
    pts.push(`${(cx + r * Math.cos(a)).toFixed(3)},${(cy + r * Math.sin(a)).toFixed(3)}`)
  }
  return pts.join(' ')
}

function star(cx: number, cy: number, r: number): string {
  const pts: string[] = []
  for (let i = 0; i < 10; i++) {
    const rr = i % 2 === 0 ? r * 1.3 : r * 0.55
    const a = -Math.PI / 2 + (Math.PI * i) / 5
    pts.push(`${(cx + rr * Math.cos(a)).toFixed(3)},${(cy + rr * Math.sin(a)).toFixed(3)}`)
  }
  return pts.join(' ')
}

export function MarkerShape({
  role,
  cx,
  cy,
  r = R,
}: {
  role: Role
  cx: number
  cy: number
  r?: number
}) {
  const { shape, color } = ROLE_STYLES[role]
  const common = { fill: color, stroke: '#0f172a', strokeWidth: 0.2 }
  switch (shape) {
    case 'star':
      return <polygon points={star(cx, cy, r)} {...common} />
    case 'triangle':
      return <polygon points={polygon(cx, cy, 3, r * 1.2, -Math.PI / 2)} {...common} />
    case 'square':
      return <rect x={cx - r * 0.85} y={cy - r * 0.85} width={r * 1.7} height={r * 1.7} {...common} />
    case 'diamond':
      return <polygon points={polygon(cx, cy, 4, r * 1.25, -Math.PI / 2)} {...common} />
    case 'circle':
      return <circle cx={cx} cy={cy} r={r * 0.9} {...common} />
    case 'hexagon':
      return <polygon points={polygon(cx, cy, 6, r * 1.1, 0)} {...common} />
  }
}

/** Marcador de jugador con su Player_Label encima (17.11). */
export default function PlayerMarker({
  role,
  label,
  x,
  y,
}: {
  role: Role
  label: string
  x: number
  y: number
}) {
  return (
    <g data-testid="player-marker" data-role={role}>
      <MarkerShape role={role} cx={x} cy={y} />
      <text
        x={x}
        y={y - R * 1.35}
        fontSize={labelSize(role)}
        textAnchor="middle"
        fill="#f8fafc"
        stroke="#0f172a"
        strokeWidth={0.12}
        paintOrder="stroke"
        data-testid="player-label"
      >
        {label}
      </text>
    </g>
  )
}
