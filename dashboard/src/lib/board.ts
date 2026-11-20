// Funciones puras de la pizarra (Coach_Board). Sin dependencias ni sintaxis
// que no se pueda borrar, para probarlas con `node --test --experimental-strip-types`.

export interface TrackPoint {
  frameId: number;
  x_norm: number;
  y_norm: number;
}

export interface BoardPlayer {
  role: string;
  is_lb?: boolean;
  track: TrackPoint[];
}

export interface ViewWindow {
  x0: number;
  x1: number;
  y0: number;
  y1: number;
}

const FIELD_WIDTH = 53.3;

/**
 * Ventana visible (13.6): contiene todas las posiciones de jugadores y balón
 * con `margin` yardas en cada borde. Se conserva la proporción 1:1 ampliando
 * el lado corto de forma simétrica, así que el margen nunca se reduce.
 */
export function viewWindow(
  players: BoardPlayer[],
  ball: TrackPoint[] = [],
  margin = 3,
): ViewWindow {
  let minX = Infinity;
  let maxX = -Infinity;
  let minY = Infinity;
  let maxY = -Infinity;
  const add = (p: TrackPoint) => {
    if (!Number.isFinite(p.x_norm) || !Number.isFinite(p.y_norm)) return;
    if (p.x_norm < minX) minX = p.x_norm;
    if (p.x_norm > maxX) maxX = p.x_norm;
    if (p.y_norm < minY) minY = p.y_norm;
    if (p.y_norm > maxY) maxY = p.y_norm;
  };
  for (const pl of players) for (const p of pl.track) add(p);
  for (const p of ball) add(p);

  if (minX === Infinity) return { x0: 0, x1: FIELD_WIDTH, y0: 0, y1: FIELD_WIDTH };

  let x0 = minX - margin;
  let x1 = maxX + margin;
  let y0 = minY - margin;
  let y1 = maxY + margin;
  const w = x1 - x0;
  const h = y1 - y0;
  if (w > h) {
    const extra = (w - h) / 2;
    y0 -= extra;
    y1 += extra;
  } else if (h > w) {
    const extra = (h - w) / 2;
    x0 -= extra;
    x1 += extra;
  }
  return { x0, x1, y0, y1 };
}

function pointAt(track: TrackPoint[], frame: number): TrackPoint | undefined {
  for (const p of track) if (p.frameId === frame) return p;
  return undefined;
}

/**
 * Avance de LB en el frame f (17.19): promedio, sobre los jugadores `is_lb`
 * con posición en `snap` y en `f`, de x_norm(snap) − x_norm(f). Nulo si no hay.
 */
export function liveLbAdvance(
  players: BoardPlayer[],
  snap: number,
  f: number,
): number | null {
  let sum = 0;
  let n = 0;
  for (const pl of players) {
    if (!pl.is_lb) continue;
    const a = pointAt(pl.track, snap);
    const b = pointAt(pl.track, f);
    if (!a || !b) continue;
    sum += a.x_norm - b.x_norm;
    n += 1;
  }
  return n === 0 ? null : sum / n;
}

/**
 * Distancia euclidiana mínima QB–Pass Rush en el frame f (17.20).
 * Nula si falta el QB, algún Pass Rush o sus posiciones en f (17.23).
 */
export function liveQbRushDist(players: BoardPlayer[], f: number): number | null {
  const qbPoint = players
    .filter((p) => p.role === "QB")
    .map((p) => pointAt(p.track, f))
    .find((p) => p !== undefined);
  if (!qbPoint) return null;
  let best: number | null = null;
  for (const pl of players) {
    if (pl.role !== "Pass Rush") continue;
    const r = pointAt(pl.track, f);
    if (!r) continue;
    const d = Math.hypot(r.x_norm - qbPoint.x_norm, r.y_norm - qbPoint.y_norm);
    if (best === null || d < best) best = d;
  }
  return best;
}

/**
 * Número de yarda para una línea en x absoluto (0 a 120, zonas de 10 yardas):
 * min(x−10, 110−x) para x múltiplo de 10 entre 20 y 100; nulo en otro caso.
 */
export function fieldYardNumber(x: number): number | null {
  if (!Number.isInteger(x) || x % 10 !== 0 || x < 20 || x > 100) return null;
  return Math.min(x - 10, 110 - x);
}
