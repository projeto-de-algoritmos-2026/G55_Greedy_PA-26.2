import type { Show } from '../types'
import { formatarDuracao, minutosParaHHMM } from '../utils/tempo'

interface Props {
  show: Show
  nomePalco: string
  cor: string
  ordem: number | undefined
  nota: number
  topo: number
  altura: number
  aoAbrirNota: () => void
  aoDefinirNota: (nota: number) => void
}

export function BlocoShow({ show, nomePalco, cor, ordem, nota, topo, altura, aoAbrirNota, aoDefinirNota }: Props) {
  const noRoteiro = ordem !== undefined
  const horario = `${minutosParaHHMM(show.inicio)} a ${minutosParaHHMM(show.fim)}`
  const compacto = altura < 60

  return (
    <button
      type="button"
      onClick={aoAbrirNota}
      onKeyDown={(e) => {
        if (/^[0-9]$/.test(e.key)) {
          e.preventDefault()
          aoDefinirNota(e.key === '0' ? 10 : Number(e.key))
        }
      }}
      aria-label={`${show.artista}, ${nomePalco}, ${horario}, ${noRoteiro ? `número ${ordem} do roteiro` : 'fora do roteiro'}, nota ${nota}`}
      style={{ top: topo + 1, height: altura - 2, ...(noRoteiro ? { backgroundColor: cor } : { borderLeftColor: cor }) }}
      className={`absolute inset-x-1 overflow-hidden rounded-lg px-2 py-1 text-left transition-[background-color,color] duration-200 ${
        noRoteiro ? 'text-noite' : 'border-l-4 bg-superficie-alta/70 text-texto-suave hover:bg-superficie-alta hover:text-texto'
      }`}
    >
      <span className="flex items-start gap-1.5">
        {noRoteiro && (
          <span className="horario mt-px grid size-5 shrink-0 place-items-center rounded-full bg-noite text-[11px] font-bold text-ipe">
            {ordem}
          </span>
        )}
        <span className={`condensado font-display leading-tight font-semibold ${compacto ? 'line-clamp-1 text-[13px]' : 'line-clamp-2 text-[15px]'}`}>
          {show.artista}
        </span>
      </span>
      {!compacto && (
        <span className={`horario mt-0.5 block text-xs ${noRoteiro ? 'text-noite/80' : ''}`}>
          {minutosParaHHMM(show.inicio)}–{minutosParaHHMM(show.fim)} · {formatarDuracao(show.fim - show.inicio)}
        </span>
      )}
      {nota > 1 && (
        <span className="absolute inset-x-2 bottom-1 h-1 rounded-full bg-black/15" aria-hidden>
          <span
            className={`block h-full rounded-full ${noRoteiro ? 'bg-noite' : 'bg-ipe'}`}
            style={{ width: `${nota * 10}%` }}
          />
        </span>
      )}
    </button>
  )
}
