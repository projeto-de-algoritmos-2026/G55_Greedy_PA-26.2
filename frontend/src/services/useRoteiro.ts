import { useEffect, useRef, useState } from 'react'
import type { RequisicaoCalculo, RoteiroResponse } from '../types'
import { api, ApiError, type Objetivo } from './api'

// Recalcula o roteiro quando objetivo, modo, delta ou notas mudam. Espera um instante para
// agrupar mudanças em sequência (como arrastar uma régua) e cancela a requisição anterior.

const ESPERA_MS = 150

export type EstadoRoteiro =
  | { status: 'carregando'; anterior?: RoteiroResponse }
  | { status: 'sucesso'; dados: RoteiroResponse; recalculando: boolean }
  | { status: 'erro'; erro: ApiError; anterior?: RoteiroResponse }

export function useRoteiro(objetivo: Objetivo, req: RequisicaoCalculo | null, tentativa: number) {
  const [estado, setEstado] = useState<EstadoRoteiro>({ status: 'carregando' })
  const ultimo = useRef<RoteiroResponse | undefined>(undefined)
  const chave = req ? JSON.stringify([objetivo, req]) : null

  useEffect(() => {
    if (!chave || !req) return
    const controle = new AbortController()
    setEstado(ultimo.current ? { status: 'sucesso', dados: ultimo.current, recalculando: true } : { status: 'carregando' })

    const timer = window.setTimeout(() => {
      api
        .roteiro(objetivo, req, controle.signal)
        .then((dados) => {
          ultimo.current = dados
          setEstado({ status: 'sucesso', dados, recalculando: false })
        })
        .catch((e: unknown) => {
          if (e instanceof DOMException && e.name === 'AbortError') return
          const erro = e instanceof ApiError ? e : new ApiError(0, String(e))
          setEstado({ status: 'erro', erro, anterior: ultimo.current })
        })
    }, ESPERA_MS)

    return () => {
      window.clearTimeout(timer)
      controle.abort()
    }
    // A chave serializada já cobre objetivo e requisição.
    // oxlint-disable-next-line react-hooks/exhaustive-deps
  }, [chave, tentativa])

  return estado
}
