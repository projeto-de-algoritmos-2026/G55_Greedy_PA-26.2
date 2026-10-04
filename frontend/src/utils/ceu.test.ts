import { describe, expect, it } from 'vitest'
import { corDoCeu, gradienteDoCeu } from './ceu'

describe('céu', () => {
  it('usa as cores das paradas nos horários exatos', () => {
    expect(corDoCeu(14 * 60)).toBe('#e8a866')
    expect(corDoCeu(20 * 60)).toBe('#2a3366')
  })

  it('fixa os extremos fora do intervalo', () => {
    expect(corDoCeu(10 * 60)).toBe('#e8a866')
    expect(corDoCeu(26 * 60)).toBe('#141c38')
  })

  it('interpola entre paradas', () => {
    const meio = corDoCeu(19 * 60 + 15)
    expect(meio).not.toBe('#6a5a9e')
    expect(meio).not.toBe('#2a3366')
  })

  it('gera um gradiente de cima para baixo cobrindo 0% a 100%', () => {
    const g = gradienteDoCeu(840, 1440, 300)
    expect(g.startsWith('linear-gradient(to bottom,')).toBe(true)
    expect(g).toContain('0.00%')
    expect(g).toContain('100.00%')
  })
})
