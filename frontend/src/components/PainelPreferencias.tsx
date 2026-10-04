import { Search, X } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'
import type { Palco, Pesos, Show } from '../types'
import { mapearCoresPalcos } from '../utils/palcos'
import { minutosParaHHMM } from '../utils/tempo'

interface Props {
  aberto: boolean
  shows: Show[]
  palcos: Palco[]
  notas: Pesos
  aoDefinirNota: (showId: string, nota: number) => void
  aoLimpar: () => void
  aoFechar: () => void
}

const normalizar = (texto: string) => texto.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()

export function PainelPreferencias({ aberto, shows, palcos, notas, aoDefinirNota, aoLimpar, aoFechar }: Props) {
  const [busca, setBusca] = useState('')
  const campoBusca = useRef<HTMLInputElement>(null)
  const cores = mapearCoresPalcos(palcos)
  const visiveis = useMemo(() => {
    const termo = normalizar(busca.trim())
    return termo ? shows.filter((s) => normalizar(s.artista).includes(termo)) : shows
  }, [busca, shows])
  const avaliados = Object.keys(notas).length

  useEffect(() => {
    if (!aberto) return
    campoBusca.current?.focus()
    const aoTeclar = (e: KeyboardEvent) => e.key === 'Escape' && aoFechar()
    document.addEventListener('keydown', aoTeclar)
    return () => document.removeEventListener('keydown', aoTeclar)
  }, [aberto, aoFechar])

  if (!aberto) return null

  return (
    <aside
      role="dialog"
      aria-label="Minhas notas"
      className="fixed top-28 right-0 bottom-0 z-40 flex w-[400px] flex-col border-l border-linha bg-superficie shadow-2xl shadow-black/50"
    >
      <div className="flex items-center justify-between px-5 pt-5">
        <h2 className="font-display text-xl font-bold">Minhas notas</h2>
        <button onClick={aoFechar} className="rounded-md p-1.5 text-texto-suave hover:bg-superficie-alta hover:text-texto" aria-label="Fechar">
          <X className="size-5" aria-hidden />
        </button>
      </div>
      <p className="px-5 pt-1 text-sm text-texto-suave">
        Dê de 1 a 10 para cada show. Em "Mais satisfação", o roteiro soma as notas. Shows sem nota valem 1.
      </p>
      <div className="flex items-center gap-2 px-5 py-4">
        <label className="flex flex-1 items-center gap-2 rounded-lg bg-noite px-3 py-2 focus-within:outline-2 focus-within:outline-ipe">
          <Search className="size-4 text-texto-suave" aria-hidden />
          <input
            ref={campoBusca}
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            placeholder="Buscar artista"
            className="w-full bg-transparent text-sm placeholder:text-texto-suave focus:outline-none"
          />
        </label>
        <button
          onClick={aoLimpar}
          disabled={avaliados === 0}
          className="rounded-lg px-3 py-2 text-sm font-medium text-texto-suave hover:text-texto disabled:opacity-40"
        >
          Limpar notas
        </button>
      </div>
      <ul className="flex-1 space-y-1 overflow-y-auto px-3 pb-5">
        {visiveis.map((s) => {
          const nota = notas[s.id] ?? 1
          return (
            <li key={s.id} className="rounded-lg px-2 py-2 hover:bg-superficie-alta/60">
              <div className="flex items-baseline justify-between gap-3">
                <span className="flex min-w-0 items-center gap-2">
                  <span className="size-2 shrink-0 rounded-full" style={{ backgroundColor: cores.get(s.palco) }} aria-hidden />
                  <span className="truncate font-medium">{s.artista}</span>
                </span>
                <span className="horario shrink-0 text-xs text-texto-suave">{minutosParaHHMM(s.inicio)}</span>
              </div>
              <div className="mt-1.5 flex items-center gap-3">
                <input
                  type="range"
                  min={1}
                  max={10}
                  value={nota}
                  onChange={(e) => aoDefinirNota(s.id, Number(e.target.value))}
                  aria-label={`Nota para ${s.artista}`}
                  className="h-1.5 flex-1 accent-[var(--color-ipe)]"
                />
                <span className={`horario w-5 text-right text-sm font-semibold ${nota > 1 ? 'text-ipe' : 'text-texto-suave'}`}>{nota}</span>
              </div>
            </li>
          )
        })}
        {visiveis.length === 0 && <li className="px-2 py-6 text-sm text-texto-suave">Nenhum artista com "{busca}".</li>}
      </ul>
    </aside>
  )
}
