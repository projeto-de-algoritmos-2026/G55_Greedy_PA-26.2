// As dependências do efeito são repassadas por quem chama, como em useEffect.
/* oxlint-disable react-hooks/exhaustive-deps */
import { useEffect, useState } from 'react'
import { ApiError } from './api'

// Estados de uma requisição: carregando, sucesso e erro; "vazio" é decidido por quem consome.
export type EstadoRequisicao<T> =
  | { status: 'carregando' }
  | { status: 'sucesso'; dados: T }
  | { status: 'erro'; erro: ApiError }

export function useRequisicao<T>(buscar: () => Promise<T>, deps: readonly unknown[]): EstadoRequisicao<T> {
  const [estado, setEstado] = useState<EstadoRequisicao<T>>({ status: 'carregando' })

  useEffect(() => {
    let ativo = true
    setEstado({ status: 'carregando' })
    buscar()
      .then((dados) => ativo && setEstado({ status: 'sucesso', dados }))
      .catch((e: unknown) => {
        if (!ativo) return
        const erro = e instanceof ApiError ? e : new ApiError(0, e instanceof Error ? e.message : String(e))
        setEstado({ status: 'erro', erro })
      })
    return () => {
      ativo = false
    }
  }, deps)

  return estado
}
