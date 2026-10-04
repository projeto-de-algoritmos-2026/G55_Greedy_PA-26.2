import { describe, expect, it } from 'vitest'
import type { Show } from '../types'
import { alturaTotal, intervaloDoDia, marcasDeHora, posicaoVertical, PX_POR_MINUTO } from './grade'

const show = (inicio: number, fim: number): Show => ({ id: 'S001', artista: 'A', palco: 'P1', inicio, fim, peso: 1 })

describe('grade', () => {
  it('arredonda o intervalo do dia para horas cheias', () => {
    expect(intervaloDoDia([show(850, 900), show(1450, 1530)])).toEqual({ inicio: 840, fim: 1560 })
  })

  it('usa um intervalo padrão sem shows', () => {
    expect(intervaloDoDia([])).toEqual({ inicio: 840, fim: 1440 })
  })

  it('converte minutos em pixels a partir do início do intervalo', () => {
    const intervalo = { inicio: 840, fim: 960 }
    expect(posicaoVertical(900, intervalo)).toBe(60 * PX_POR_MINUTO)
    expect(alturaTotal(intervalo)).toBe(120 * PX_POR_MINUTO)
  })

  it('lista as horas cheias incluindo as pontas', () => {
    expect(marcasDeHora({ inicio: 840, fim: 1020 })).toEqual([840, 900, 960, 1020])
  })
})
