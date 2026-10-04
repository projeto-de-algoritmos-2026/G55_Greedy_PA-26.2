import type { Palco } from '../types'
import { CORES_PALCO } from './cores'

/** Cor de cada palco pela ordem em que aparece no palcos.json (no máximo cinco cores). */
export function mapearCoresPalcos(palcos: readonly Palco[]): Map<string, string> {
  return new Map(palcos.map((p, i) => [p.codigo, CORES_PALCO[i % CORES_PALCO.length]!]))
}
