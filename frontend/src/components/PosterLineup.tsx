import { Fragment } from 'react'
import type { Palco, Show } from '../types'
import { mapearCoresPalcos } from '../utils/palcos'

// Pôster de lineup gerado da grade: quem toca por mais tempo aparece maior, como num cartaz de festival.

const NIVEIS = [
  { quantidade: 3, classe: 'text-[3.25rem] leading-[1.05] font-extrabold text-texto' },
  { quantidade: 8, classe: 'text-[2rem] leading-tight font-bold text-texto' },
  { quantidade: Infinity, classe: 'text-xl leading-snug font-semibold text-texto-suave' },
] as const

export function PosterLineup({ shows, palcos }: { shows: Show[]; palcos: Palco[] }) {
  const cores = mapearCoresPalcos(palcos)
  const ordenados = [...shows].sort((a, b) => b.fim - b.inicio - (a.fim - a.inicio) || b.inicio - a.inicio)
  const linhas = NIVEIS.map((nivel, i) => {
    const inicio = NIVEIS.slice(0, i).reduce((soma, n) => soma + n.quantidade, 0)
    return { classe: nivel.classe, shows: ordenados.slice(inicio, inicio + nivel.quantidade) }
  })

  return (
    <div className="space-y-3" aria-label="Lineup do dia">
      {linhas.map(({ classe, shows: linha }, i) => {
        if (linha.length === 0) return null
        return (
          <p key={i} className={`condensado font-display ${classe}`}>
            {linha.map((s, j) => (
              <Fragment key={s.id}>
                <span className="whitespace-nowrap">
                  {s.artista}
                  {j < linha.length - 1 && (
                    <span
                      className="mx-[0.3em] inline-block size-[0.28em] -translate-y-[0.15em] rounded-full align-middle"
                      style={{ backgroundColor: cores.get(s.palco) }}
                      aria-hidden
                    />
                  )}
                </span>{' '}
              </Fragment>
            ))}
          </p>
        )
      })}
    </div>
  )
}
