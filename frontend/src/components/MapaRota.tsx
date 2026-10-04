import { useMemo } from 'react'
import type { Palco, Show } from '../types'
import { COR } from '../utils/cores'
import { comprimento, marcadoresDaRota, pontosDaRota } from '../utils/rota'

// O mapa SVG do festival tem viewBox 1000 × 625; a camada da rota usa o mesmo sistema.
const LARGURA = 1000
const ALTURA = 625
// Os marcadores ficam acima da caixa do palco para não cobrir o nome dele.
const DESLOCAMENTO_MARCADOR = -62

interface Props {
  urlMapa: string
  palcos: Palco[]
  roteiro: Show[]
}

export function MapaRota({ urlMapa, palcos, roteiro }: Props) {
  const porCodigo = useMemo(() => new Map(palcos.map((p) => [p.codigo, p])), [palcos])
  const pontos = pontosDaRota(roteiro, porCodigo, LARGURA, ALTURA).map((p) => ({ ...p, y: p.y + DESLOCAMENTO_MARCADOR }))
  const marcadores = marcadoresDaRota(roteiro, porCodigo, LARGURA, ALTURA)
  const total = comprimento(pontos)
  // Uma chave nova a cada roteiro reinicia a animação do traço.
  const chave = roteiro.map((s) => s.id).join('-')

  return (
    <figure className="relative aspect-[1000/625] overflow-hidden rounded-xl border border-linha">
      <img src={urlMapa} alt="" className="absolute inset-0 size-full" />
      <svg viewBox={`0 0 ${LARGURA} ${ALTURA}`} className="absolute inset-0 size-full" role="img" aria-label={`Rota com ${roteiro.length} shows em ${marcadores.length} palcos`}>
        {pontos.length > 1 && (
          <polyline
            key={chave}
            points={pontos.map((p) => `${p.x},${p.y}`).join(' ')}
            fill="none"
            stroke={COR.ipe}
            strokeWidth={7}
            strokeLinecap="round"
            strokeLinejoin="round"
            className="animar-rota"
            style={{ '--comprimento': total } as React.CSSProperties}
          />
        )}
        {marcadores.map((m) => {
          const rotulo = m.numeros.join(' · ')
          const largura = Math.max(52, 24 + rotulo.length * 19)
          return (
            <g key={m.palco} transform={`translate(${m.x}, ${m.y + DESLOCAMENTO_MARCADOR})`}>
              <rect x={-largura / 2} y={-26} width={largura} height={52} rx={26} fill={COR.ipe} stroke={COR.noite} strokeWidth={4} />
              <text textAnchor="middle" dy="0.35em" fontSize={32} fontWeight={700} fill={COR.noite} fontFamily="Instrument Sans Variable, sans-serif">
                {rotulo}
              </text>
            </g>
          )
        })}
      </svg>
      <figcaption className="sr-only">Mapa do festival com a rota numerada na ordem do roteiro.</figcaption>
    </figure>
  )
}
