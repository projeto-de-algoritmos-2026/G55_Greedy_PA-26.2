// Geometria da grade: o tempo corre na vertical, um palco por coluna.

import type { Show } from '../types'

export const PX_POR_MINUTO = 1.6

export interface Intervalo {
  inicio: number
  fim: number
}

/** Intervalo visível do dia, arredondado para horas cheias. */
export function intervaloDoDia(shows: readonly Show[]): Intervalo {
  if (shows.length === 0) return { inicio: 14 * 60, fim: 24 * 60 }
  const inicio = Math.min(...shows.map((s) => s.inicio))
  const fim = Math.max(...shows.map((s) => s.fim))
  return { inicio: Math.floor(inicio / 60) * 60, fim: Math.ceil(fim / 60) * 60 }
}

export function posicaoVertical(minuto: number, intervalo: Intervalo): number {
  return (minuto - intervalo.inicio) * PX_POR_MINUTO
}

export function alturaTotal(intervalo: Intervalo): number {
  return (intervalo.fim - intervalo.inicio) * PX_POR_MINUTO
}

/** Minutos de cada hora cheia dentro do intervalo, incluindo as pontas. */
export function marcasDeHora(intervalo: Intervalo): number[] {
  const marcas: number[] = []
  for (let m = intervalo.inicio; m <= intervalo.fim; m += 60) marcas.push(m)
  return marcas
}
