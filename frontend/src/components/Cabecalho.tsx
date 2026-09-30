import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

export function Cabecalho({ children }: { children?: ReactNode }) {
  return (
    <header className="border-b border-borda bg-superficie">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 px-6">
        <Link to="/" className="text-lg font-semibold tracking-tight">
          Rota<span className="text-palco-1">Fest</span>
        </Link>
        {children}
      </div>
    </header>
  )
}
