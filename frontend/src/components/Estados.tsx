import { RotateCcw } from 'lucide-react'
import type { ReactNode } from 'react'
import type { ApiError } from '../services/api'

export function Esqueleto({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-superficie-alta/70 ${className}`} aria-hidden />
}

export function Carregando({ texto, children }: { texto: string; children?: ReactNode }) {
  return (
    <div role="status" aria-label={texto} className="h-full">
      {children ?? (
        <div className="space-y-3 p-6">
          <Esqueleto className="h-5 w-1/3" />
          <Esqueleto className="h-24" />
          <Esqueleto className="h-24" />
        </div>
      )}
    </div>
  )
}

export function Vazio({ titulo, descricao }: { titulo: string; descricao?: string }) {
  return (
    <div className="flex h-full flex-col items-start justify-center gap-1 p-6">
      <p className="font-display text-lg font-semibold">{titulo}</p>
      {descricao && <p className="max-w-sm text-sm text-texto-suave">{descricao}</p>}
    </div>
  )
}

export function Erro({ erro, aoTentarDeNovo }: { erro: ApiError; aoTentarDeNovo?: () => void }) {
  return (
    <div role="alert" className="flex flex-col items-start gap-3 p-6">
      <p className="max-w-md font-medium text-erro">{erro.message}</p>
      {erro.erros.length > 0 && (
        <ul className="space-y-1 text-sm text-texto-suave">
          {erro.erros.map((e) => (
            <li key={`${e.linha}-${e.coluna}`}>
              Linha {e.linha}, coluna <code className="text-texto">{e.coluna}</code>: {e.mensagem}
            </li>
          ))}
        </ul>
      )}
      {erro.campos.length > 1 && (
        <ul className="space-y-1 text-sm text-texto-suave">
          {erro.campos.map((e) => (
            <li key={e.campo}>
              <code className="text-texto">{e.campo}</code>: {e.mensagem}
            </li>
          ))}
        </ul>
      )}
      {aoTentarDeNovo && (
        <button
          onClick={aoTentarDeNovo}
          className="inline-flex items-center gap-2 rounded-lg border border-linha px-3 py-1.5 text-sm font-medium hover:bg-superficie-alta"
        >
          <RotateCcw className="size-4" aria-hidden />
          Tentar de novo
        </button>
      )}
    </div>
  )
}
