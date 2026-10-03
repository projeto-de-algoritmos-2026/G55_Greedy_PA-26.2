// Cliente tipado da API.

import type { ErroApi, ErroCampo, ErroLinha, FestivalResumo, GradeResponse } from '../types'

const BASE_URL = `${import.meta.env.VITE_API_URL ?? ''}/api`

/** Erro com a mensagem do backend (nunca uma mensagem genérica). */
export class ApiError extends Error {
  readonly status: number
  readonly erros: ErroLinha[]
  readonly campos: ErroCampo[]

  constructor(status: number, mensagem: string, erros: ErroLinha[] = [], campos: ErroCampo[] = []) {
    super(mensagem)
    this.name = 'ApiError'
    this.status = status
    this.erros = erros
    this.campos = campos
  }
}

function ehErroLinha(erro: ErroLinha | ErroCampo): erro is ErroLinha {
  return 'linha' in erro
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
    if (ehErroApi(corpo)) {
      const erros: (ErroLinha | ErroCampo)[] = corpo.erros ?? []
      throw new ApiError(
        resposta.status,
        corpo.detail,
        erros.filter(ehErroLinha),
        erros.filter((e): e is ErroCampo => !ehErroLinha(e)),
      )
    }
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
