import { describe, expect, it } from 'vitest'
import { COR, CORES_PALCO } from './cores'
import { razaoContraste } from './contraste'

const MINIMO = 4.5

describe('contraste da paleta', () => {
  it.each([
    ['texto sobre noite', COR.texto, COR.noite],
    ['texto sobre superfície', COR.texto, COR.superficie],
    ['texto sobre superfície alta', COR.texto, COR.superficieAlta],
    ['texto suave sobre noite', COR.textoSuave, COR.noite],
    ['texto suave sobre superfície', COR.textoSuave, COR.superficie],
    ['texto suave sobre superfície alta', COR.textoSuave, COR.superficieAlta],
    ['ipê sobre noite', COR.ipe, COR.noite],
    ['ipê sobre superfície', COR.ipe, COR.superficie],
    ['noite sobre ipê', COR.noite, COR.ipe],
  ])('%s atinge 4,5:1', (_, frente, fundo) => {
    expect(razaoContraste(frente, fundo)).toBeGreaterThanOrEqual(MINIMO)
  })

  it.each(CORES_PALCO)('texto noite sobre o palco %s atinge 4,5:1', (cor) => {
    expect(razaoContraste(COR.noite, cor)).toBeGreaterThanOrEqual(MINIMO)
  })

  it('preto e branco dão 21:1', () => {
    expect(razaoContraste('#000000', '#ffffff')).toBeCloseTo(21, 5)
  })
})
