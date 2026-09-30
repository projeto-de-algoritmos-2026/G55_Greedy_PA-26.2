// Cliente tipado da API (SPEC 4). Nesta fase cobre apenas festivais e grade;
// os endpoints de cálculo entram na T-601.

import type { ErroApi, ErroLinha, FestivalResumo, GradeResponse } from '../types'

const BASE_URL = `${import.meta.env.VITE_API_URL ?? ''}/api`

/** Erro com a mensagem do backend (SPEC 6.3: nada de mensagem genérica). */
export class ApiError extends Error {
  readonly status: number
  readonly erros: ErroLinha[]

  constructor(status: number, mensagem: string, erros: ErroLinha[] = []) {
    super(mensagem)
    this.name = 'ApiError'
    this.status = status
    this.erros = erros
  }
}

function ehErroApi(corpo: unknown): corpo is ErroApi {
  return typeof corpo === 'object' && corpo !== null && typeof (corpo as ErroApi).detail === 'string'
}

async function requisitar<T>(caminho: string, init?: RequestInit): Promise<T> {
  let resposta: Response
  try {
    resposta = await fetch(`${BASE_URL}${caminho}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    })
  } catch {
    throw new ApiError(0, 'Não foi possível conectar ao backend. Verifique se ele está rodando na porta 8000.')
  }

  const corpo: unknown = await resposta.json().catch(() => null)
  if (!resposta.ok) {
    if (ehErroApi(corpo)) throw new ApiError(resposta.status, corpo.detail, corpo.erros)
    throw new ApiError(resposta.status, `O backend respondeu ${resposta.status} sem detalhes.`)
  }
  return corpo as T
}

export const api = {
  listarFestivais: () => requisitar<FestivalResumo[]>('/festivais'),

  obterGrade: (festivalId: string, dia: number) =>
    requisitar<GradeResponse>(`/festivais/${encodeURIComponent(festivalId)}/grade?dia=${dia}`),

  urlMapa: (festivalId: string) => `${BASE_URL}/festivais/${encodeURIComponent(festivalId)}/mapa`,
}
