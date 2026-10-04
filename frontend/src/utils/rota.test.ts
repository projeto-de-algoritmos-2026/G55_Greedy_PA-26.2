import { describe, expect, it } from 'vitest'
import type { Palco, Show } from '../types'
import { comprimento, marcadoresDaRota, pontosDaRota } from './rota'

const palcos = new Map<string, Palco>([
  ['P1', { codigo: 'P1', nome: 'Um', x: 0, y: 0 }],
  ['P2', { codigo: 'P2', nome: 'Dois', x: 0.3, y: 0.4 }],
])
const show = (id: string, palco: string): Show => ({ id, artista: id, palco, inicio: 0, fim: 1, peso: 1 })

describe('rota', () => {
  const roteiro = [show('S001', 'P1'), show('S002', 'P1'), show('S003', 'P2'), show('S004', 'P1')]

  it('não repete o ponto para shows seguidos no mesmo palco', () => {
    expect(pontosDaRota(roteiro, palcos, 100, 100)).toEqual([
      { x: 0, y: 0 },
      { x: 30, y: 40 },
      { x: 0, y: 0 },
    ])
  })

  it('agrupa os números do roteiro por palco', () => {
    const marcadores = marcadoresDaRota(roteiro, palcos, 100, 100)
    expect(marcadores.map((m) => [m.palco, m.numeros])).toEqual([
      ['P1', [1, 2, 4]],
      ['P2', [3]],
    ])
  })

  it('soma o comprimento dos segmentos', () => {
    expect(comprimento(pontosDaRota(roteiro, palcos, 100, 100))).toBe(100)
    expect(comprimento([])).toBe(0)
  })

  it('ignora palcos desconhecidos', () => {
    expect(pontosDaRota([show('S009', 'P9')], palcos, 100, 100)).toEqual([])
  })
})
