import { Minus, Plus } from 'lucide-react'
import type { Objetivo } from '../services/api'
import type { ModoDeslocamento } from '../types'

interface OpcaoSegmento<T extends string> {
  valor: T
  rotulo: string
}

function Segmentado<T extends string>({ rotulo, opcoes, valor, aoMudar }: {
  rotulo: string
  opcoes: OpcaoSegmento<T>[]
  valor: T
  aoMudar: (valor: T) => void
}) {
  return (
    <div role="radiogroup" aria-label={rotulo} className="inline-flex rounded-lg bg-superficie p-0.5">
      {opcoes.map((o) => (
        <button
          key={o.valor}
          role="radio"
          aria-checked={o.valor === valor}
          onClick={() => aoMudar(o.valor)}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
            o.valor === valor ? 'bg-superficie-alta text-texto shadow-sm' : 'text-texto-suave hover:text-texto'
          }`}
        >
          {o.rotulo}
        </button>
      ))}
    </div>
  )
}

export const DELTA_MAXIMO = 120

interface Props {
  objetivo: Objetivo
  modo: ModoDeslocamento
  delta: number
  aoMudarObjetivo: (objetivo: Objetivo) => void
  aoMudarModo: (modo: ModoDeslocamento) => void
  aoMudarDelta: (delta: number) => void
}

export function ControlesOtimizacao({ objetivo, modo, delta, aoMudarObjetivo, aoMudarModo, aoMudarDelta }: Props) {
  const ajustar = (valor: number) => aoMudarDelta(Math.max(0, Math.min(DELTA_MAXIMO, valor)))
  return (
    <div className="flex flex-wrap items-center gap-3">
      <Segmentado
        rotulo="Objetivo do roteiro"
        valor={objetivo}
        aoMudar={aoMudarObjetivo}
        opcoes={[
          { valor: 'maximo-shows', rotulo: 'Mais shows' },
          { valor: 'maxima-satisfacao', rotulo: 'Mais satisfação' },
        ]}
      />
      <Segmentado
        rotulo="Tempo de deslocamento"
        valor={modo}
        aoMudar={aoMudarModo}
        opcoes={[
          { valor: 'uniforme', rotulo: 'Tempo fixo entre shows' },
          { valor: 'matricial', rotulo: 'Distância real entre palcos' },
        ]}
      />
      {modo === 'uniforme' && (
        <div className="inline-flex items-center rounded-lg bg-superficie p-0.5" role="group" aria-label="Minutos entre shows">
          <button onClick={() => ajustar(delta - 1)} className="rounded-md p-1.5 text-texto-suave hover:bg-superficie-alta hover:text-texto" aria-label="Menos um minuto">
            <Minus className="size-4" aria-hidden />
          </button>
          <label className="horario flex items-baseline gap-1 px-1 text-sm">
            <input
              type="number"
              min={0}
              max={DELTA_MAXIMO}
              value={delta}
              onChange={(e) => ajustar(Number(e.target.value) || 0)}
              className="w-9 bg-transparent text-right font-semibold [appearance:textfield] focus:outline-none [&::-webkit-inner-spin-button]:appearance-none"
              aria-label="Minutos entre shows"
            />
            <span className="text-texto-suave">min</span>
          </label>
          <button onClick={() => ajustar(delta + 1)} className="rounded-md p-1.5 text-texto-suave hover:bg-superficie-alta hover:text-texto" aria-label="Mais um minuto">
            <Plus className="size-4" aria-hidden />
          </button>
        </div>
      )}
    </div>
  )
}
