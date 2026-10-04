import { Footprints } from 'lucide-react'
import { Fragment } from 'react'
import type { Deslocamento, Palco, Show } from '../types'
import { mapearCoresPalcos } from '../utils/palcos'
import { minutosParaHHMM, viraDia } from '../utils/tempo'

interface Props {
  roteiro: Show[]
  deslocamentos: Deslocamento[]
  palcos: Palco[]
}

function Caminhada({ d }: { d: Deslocamento }) {
  const mesmoPalco = d.palco_origem === d.palco_destino
  const semFolga = d.folga_min === 0
  return (
    <li className={`ml-3 flex items-center gap-2 border-l-2 border-dashed py-2 pl-6 text-sm ${semFolga ? 'border-ipe text-ipe' : 'border-linha text-texto-suave'}`}>
      <Footprints className="size-4 shrink-0" aria-hidden />
      {semFolga ? (
        <span>
          <strong className="font-semibold">Sem folga:</strong> saia assim que acabar{d.custo_min > 0 ? ` (${d.custo_min} min a pé)` : ''}
        </span>
      ) : (
        <span className="horario">
          {mesmoPalco ? 'Mesmo palco' : `${d.custo_min} min a pé`} · folga {d.folga_min} min
        </span>
      )}
    </li>
  )
}

export function TimelineRoteiro({ roteiro, deslocamentos, palcos }: Props) {
  const cores = mapearCoresPalcos(palcos)
  const nomes = new Map(palcos.map((p) => [p.codigo, p.nome]))
  return (
    <ol aria-label="Roteiro em ordem cronológica">
      {roteiro.map((s, i) => (
        <Fragment key={s.id}>
          <li className="flex items-start gap-3">
            <span className="horario mt-0.5 grid size-7 shrink-0 place-items-center rounded-full bg-ipe text-sm font-bold text-noite">
              {i + 1}
            </span>
            <div className="min-w-0">
              <p className="horario text-sm text-texto-suave">
                {minutosParaHHMM(s.inicio)}–{minutosParaHHMM(s.fim)}
                {viraDia(s.inicio) && ' da madrugada'}
              </p>
              <p className="truncate font-display text-[17px] leading-snug font-semibold">{s.artista}</p>
              <p className="flex items-center gap-1.5 text-sm text-texto-suave">
                <span className="size-2 rounded-full" style={{ backgroundColor: cores.get(s.palco) }} aria-hidden />
                {nomes.get(s.palco) ?? s.palco}
              </p>
            </div>
          </li>
          {deslocamentos[i] && <Caminhada d={deslocamentos[i]} />}
        </Fragment>
      ))}
    </ol>
  )
}
