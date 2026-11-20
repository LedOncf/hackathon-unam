import type { Role } from '../api/types'
import { ROLE_STYLES } from './PlayerMarker'

const ROLES: Role[] = ['QB', 'Pass Route', 'Pass Block', 'Pass Rush', 'Coverage', 'LB']

/** Leyenda con los 6 roles y su símbolo (13.3). */
export default function Legend() {
  return (
    <ul className="flex flex-wrap gap-x-4 gap-y-1 text-sm" aria-label="Leyenda de roles" data-testid="legend">
      {ROLES.map((r) => (
        <li key={r} className="flex items-center gap-1.5">
          <span aria-hidden="true" style={{ color: ROLE_STYLES[r].color }} className="text-base leading-none">
            {ROLE_STYLES[r].symbol}
          </span>
          <span>{r}</span>
        </li>
      ))}
    </ul>
  )
}
