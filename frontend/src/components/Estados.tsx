import type { ApiError } from '../services/api'

export function Carregando({ texto = 'Carregando…' }: { texto?: string }) {
  return (
    <div role="status" className="flex items-center gap-3 py-12 text-texto-suave">
      <span className="size-4 animate-spin rounded-full border-2 border-borda border-t-palco-1" aria-hidden />
      {texto}
    </div>
  )
}

export function Vazio({ titulo, descricao }: { titulo: string; descricao?: string }) {
  return (
    <div className="rounded-lg border border-dashed border-borda px-6 py-12 text-center">
      <p className="font-medium">{titulo}</p>
      {descricao && <p className="mt-1 text-sm text-texto-suave">{descricao}</p>}
    </div>
  )
}

export function Erro({ erro }: { erro: ApiError }) {
  return (
    <div role="alert" className="rounded-lg border border-erro/30 bg-erro/5 px-5 py-4">
      <p className="font-medium text-erro">{erro.message}</p>
      {erro.erros.length > 0 && (
        <ul className="mt-2 space-y-1 text-sm text-texto-suave">
          {erro.erros.map((e) => (
            <li key={`${e.linha}-${e.coluna}`}>
              Linha {e.linha}, coluna <code>{e.coluna}</code>: {e.mensagem}
            </li>
          ))}
        </ul>
      )}
      {erro.campos.length > 1 && (
        <ul className="mt-2 space-y-1 text-sm text-texto-suave">
          {erro.campos.map((e) => (
            <li key={e.campo}>
              <code>{e.campo}</code>: {e.mensagem}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
