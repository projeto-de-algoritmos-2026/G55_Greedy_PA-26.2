import type { Palco } from '../types'

// Classes literais para o Tailwind detectar (SPEC 6.4: no máximo cinco cores, uma por palco).
const FUNDOS = ['bg-palco-1', 'bg-palco-2', 'bg-palco-3', 'bg-palco-4', 'bg-palco-5'] as const
const TEXTOS = ['text-palco-1', 'text-palco-2', 'text-palco-3', 'text-palco-4', 'text-palco-5'] as const

export interface CoresPalco {
  fundo: string
  texto: string
}

/** Cor de cada palco pela ordem em que aparece no palcos.json. */
export function mapearCoresPalcos(palcos: Palco[]): Map<string, CoresPalco> {
  return new Map(
    palcos.map((p, i) => [p.codigo, { fundo: FUNDOS[i % FUNDOS.length] ?? 'bg-descartado', texto: TEXTOS[i % TEXTOS.length] ?? 'text-descartado' }]),
  )
}
