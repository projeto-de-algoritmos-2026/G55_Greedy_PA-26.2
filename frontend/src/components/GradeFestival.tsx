import { useCallback, useMemo, useState } from 'react'
import type { Palco, Pesos, Show } from '../types'
import { gradienteDoCeu } from '../utils/ceu'
import { alturaTotal, intervaloDoDia, marcasDeHora, posicaoVertical, PX_POR_MINUTO } from '../utils/grade'
import { mapearCoresPalcos } from '../utils/palcos'
import { minutosParaHHMM, viraDia } from '../utils/tempo'
import { BlocoShow } from './BlocoShow'
import { PopoverNota } from './PopoverNota'

interface Props {
  palcos: Palco[]
  shows: Show[]
  /** Posição (a partir de 1) de cada show no roteiro atual. */
  ordem: ReadonlyMap<string, number>
  notas: Pesos
  aoDefinirNota: (showId: string, nota: number) => void
}

const LARGURA_REGUA = 64

export function GradeFestival({ palcos, shows, ordem, notas, aoDefinirNota }: Props) {
  const [editando, setEditando] = useState<string | null>(null)
  const fechar = useCallback(() => setEditando(null), [])
  const intervalo = useMemo(() => intervaloDoDia(shows), [shows])
  const cores = useMemo(() => mapearCoresPalcos(palcos), [palcos])
  const altura = alturaTotal(intervalo)
  const ceu = gradienteDoCeu(intervalo.inicio, intervalo.fim)
  const colunas = `${LARGURA_REGUA}px repeat(${palcos.length}, minmax(0, 1fr))`

  return (
    <div className="relative">
      <div className="sticky top-0 z-10 grid border-b border-linha bg-noite/95 backdrop-blur" style={{ gridTemplateColumns: colunas }}>
        <div />
        {palcos.map((p) => (
          <div key={p.codigo} className="flex items-center gap-2 px-2 py-3 text-sm font-semibold">
            <span className="size-2.5 shrink-0 rounded-full" style={{ backgroundColor: cores.get(p.codigo) }} aria-hidden />
            <span className="truncate">{p.nome}</span>
          </div>
        ))}
      </div>

      <div className="relative grid" style={{ gridTemplateColumns: colunas, height: altura }}>
        {/* O céu: faixa na régua e um véu muito leve por trás dos palcos. */}
        <div className="pointer-events-none absolute inset-0 opacity-[0.07]" style={{ backgroundImage: ceu }} aria-hidden />

        <div className="relative">
          <div className="absolute top-0 right-2 bottom-0 w-1.5 rounded-full" style={{ backgroundImage: ceu }} aria-hidden />
          {marcasDeHora(intervalo).map((m) => (
            <span
              key={m}
              className={`horario absolute right-5 text-xs text-texto-suave ${m === intervalo.inicio ? 'translate-y-1' : '-translate-y-1/2'}`}
              style={{ top: posicaoVertical(m, intervalo) }}
            >
              {minutosParaHHMM(m)}
              {viraDia(m) && <span className="sr-only"> da madrugada</span>}
            </span>
          ))}
        </div>

        {marcasDeHora(intervalo).map((m) => (
          <div
            key={`linha-${m}`}
            className="pointer-events-none absolute right-0 border-t border-linha/60"
            style={{ top: posicaoVertical(m, intervalo), left: LARGURA_REGUA }}
            aria-hidden
          />
        ))}

        {palcos.map((p, indice) => (
          <div key={p.codigo} className="relative border-l border-linha/40">
            {shows
              .filter((s) => s.palco === p.codigo)
              .map((s) => {
                const topo = posicaoVertical(s.inicio, intervalo)
                const alturaBloco = (s.fim - s.inicio) * PX_POR_MINUTO
                const nota = notas[s.id] ?? 1
                return (
                  <div key={s.id}>
                    <BlocoShow
                      show={s}
                      nomePalco={p.nome}
                      cor={cores.get(p.codigo) ?? '#888888'}
                      ordem={ordem.get(s.id)}
                      nota={nota}
                      topo={topo}
                      altura={alturaBloco}
                      aoAbrirNota={() => setEditando(s.id)}
                      aoDefinirNota={(n) => aoDefinirNota(s.id, n)}
                    />
                    {editando === s.id && (
                      <PopoverNota
                        artista={s.artista}
                        nota={nota}
                        aoEscolher={(n) => aoDefinirNota(s.id, n)}
                        aoFechar={fechar}
                        style={{ top: topo + Math.min(alturaBloco, 72), ...(indice >= palcos.length / 2 ? { right: 4 } : { left: 4 }) }}
                      />
                    )}
                  </div>
                )
              })}
          </div>
        ))}
      </div>
    </div>
  )
}
