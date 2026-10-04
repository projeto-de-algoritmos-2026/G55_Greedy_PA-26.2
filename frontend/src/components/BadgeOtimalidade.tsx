import { ShieldAlert, ShieldCheck } from 'lucide-react'
import type { Estrategia } from '../types'
import { ESTRATEGIAS } from '../utils/estrategias'

interface Props {
  otimo: boolean
  estrategia: Estrategia
  recalculando?: boolean
}

/** Sempre visível quando há um resultado: diz se o roteiro é comprovadamente o melhor possível. */
export function BadgeOtimalidade({ otimo, estrategia, recalculando = false }: Props) {
  const { nome, explicacao } = ESTRATEGIAS[estrategia]
  const Icone = otimo ? ShieldCheck : ShieldAlert
  return (
    <div
      className={`group relative inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm font-medium transition-opacity ${
        otimo ? 'border-ipe/40 text-ipe' : 'border-erro/50 text-erro'
      } ${recalculando ? 'opacity-50' : ''}`}
      tabIndex={0}
      aria-describedby="explicacao-estrategia"
    >
      <Icone className="size-4" aria-hidden />
      {otimo ? 'Ótimo garantido' : 'Sem garantia de otimalidade'}
      <span
        id="explicacao-estrategia"
        role="tooltip"
        className="pointer-events-none absolute top-full right-0 z-30 mt-2 w-72 rounded-lg border border-linha bg-superficie-alta p-3 text-left text-sm font-normal text-texto opacity-0 shadow-xl shadow-black/30 transition-opacity group-hover:opacity-100 group-focus:opacity-100"
      >
        <span className="block font-semibold">{nome}</span>
        <span className="mt-1 block text-texto-suave">{explicacao}</span>
      </span>
    </div>
  )
}
