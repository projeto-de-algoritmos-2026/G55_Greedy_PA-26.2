// Rota desenhada sobre o mapa: um ponto por troca de palco, números agrupados por palco.

import type { Palco, Show } from '../types'

export interface Ponto {
  x: number
  y: number
}

export interface Marcador extends Ponto {
  palco: string
  /** Posições (a partir de 1) dos shows do roteiro neste palco, em ordem cronológica. */
  numeros: number[]
}

/** Converte coordenadas relativas (0 a 1) para o sistema do viewBox do mapa. */
export function projetar(palco: Palco, largura: number, altura: number): Ponto {
  return { x: palco.x * largura, y: palco.y * altura }
}

/** Pontos da polilinha na ordem do roteiro, sem repetir shows seguidos no mesmo palco. */
export function pontosDaRota(roteiro: readonly Show[], palcos: ReadonlyMap<string, Palco>, largura: number, altura: number): Ponto[] {
  const pontos: Ponto[] = []
  let anterior: string | undefined
  for (const show of roteiro) {
    const palco = palcos.get(show.palco)
    if (!palco || show.palco === anterior) continue
    pontos.push(projetar(palco, largura, altura))
    anterior = show.palco
  }
  return pontos
}

/** Um marcador por palco visitado, com todos os números de ordem dos shows nele. */
export function marcadoresDaRota(roteiro: readonly Show[], palcos: ReadonlyMap<string, Palco>, largura: number, altura: number): Marcador[] {
  const porPalco = new Map<string, Marcador>()
  roteiro.forEach((show, i) => {
    const palco = palcos.get(show.palco)
    if (!palco) return
    const marcador = porPalco.get(show.palco) ?? { palco: show.palco, numeros: [], ...projetar(palco, largura, altura) }
    marcador.numeros.push(i + 1)
    porPalco.set(show.palco, marcador)
  })
  return [...porPalco.values()]
}

/** Comprimento total da polilinha, usado na animação do traço. */
export function comprimento(pontos: readonly Ponto[]): number {
  let total = 0
  for (let i = 1; i < pontos.length; i++) {
    total += Math.hypot(pontos[i]!.x - pontos[i - 1]!.x, pontos[i]!.y - pontos[i - 1]!.y)
  }
  return total
}
