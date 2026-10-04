import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

function Marca() {
  // Três palcos ligados por uma rota: o produto em um glifo.
  return (
    <svg viewBox="0 0 28 20" className="h-5 w-7" aria-hidden>
      <polyline points="3,15 13,5 24,13" fill="none" stroke="var(--color-ipe)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="3" cy="15" r="2.6" fill="var(--color-ipe)" />
      <circle cx="13" cy="5" r="2.6" fill="var(--color-ipe)" />
      <circle cx="24" cy="13" r="2.6" fill="var(--color-ipe)" />
    </svg>
  )
}

export function Cabecalho({ children }: { children?: ReactNode }) {
  return (
    <header className="border-b border-linha">
      <div className="flex h-14 items-center gap-6 px-6">
        <Link to="/" className="flex items-center gap-2.5 font-display text-lg font-bold tracking-tight">
          <Marca />
          RotaFest
        </Link>
        {children}
      </div>
    </header>
  )
}
