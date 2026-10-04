import { useEffect, useRef } from 'react'

interface Props {
  artista: string
  nota: number
  aoEscolher: (nota: number) => void
  aoFechar: () => void
  style?: React.CSSProperties
}

/** Régua de 1 a 10 para a nota de um show. Fecha com Esc ou clique fora. */
export function PopoverNota({ artista, nota, aoEscolher, aoFechar, style }: Props) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    ref.current?.querySelector<HTMLButtonElement>('[aria-checked="true"]')?.focus()
    const aoClicarFora = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) aoFechar()
    }
    const aoTeclar = (e: KeyboardEvent) => e.key === 'Escape' && aoFechar()
    document.addEventListener('mousedown', aoClicarFora)
    document.addEventListener('keydown', aoTeclar)
    return () => {
      document.removeEventListener('mousedown', aoClicarFora)
      document.removeEventListener('keydown', aoTeclar)
    }
  }, [aoFechar])

  return (
    <div
      ref={ref}
      style={style}
      className="absolute z-20 w-64 rounded-xl border border-linha bg-superficie-alta p-3 shadow-2xl shadow-black/40"
    >
      <p className="truncate font-display font-semibold">{artista}</p>
      <p className="mb-2 text-sm text-texto-suave">Quanto você quer ver?</p>
      <div role="radiogroup" aria-label={`Nota para ${artista}`} className="grid grid-cols-10 gap-1">
        {Array.from({ length: 10 }, (_, i) => i + 1).map((n) => (
          <button
            key={n}
            role="radio"
            aria-checked={n === nota}
            onClick={() => {
              aoEscolher(n)
              aoFechar()
            }}
            className={`horario rounded-md py-1.5 text-sm font-semibold transition-colors ${
              n === nota ? 'bg-ipe text-noite' : n < nota ? 'bg-ipe/25 text-texto' : 'bg-superficie text-texto-suave hover:text-texto'
            }`}
          >
            {n}
          </button>
        ))}
      </div>
    </div>
  )
}
