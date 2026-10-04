// Cliente tipado da API.

import type {
  ComparativoResponse,
  DimensionamentoResponse,
  ErroApi,
  ErroCampo,
  ErroLinha,
  FestivalResumo,
  GradeResponse,
  ImportarResponse,
  RequisicaoCalculo,
  RequisicaoValidar,
  RoteiroResponse,
  ValidarResponse,
} from '../types'

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

async function requisitar<T>(caminho: string, init: RequestInit = {}): Promise<T> {
  let resposta: Response
  try {
    resposta = await fetch(`${BASE_URL}${caminho}`, init)
  } catch (e) {
    // Cancelamentos voltam como estão, para quem chamou poder ignorá-los.
    if (e instanceof DOMException && e.name === 'AbortError') throw e
    throw new ApiError(0, 'Não foi possível conectar ao backend. Rode docker compose up ou inicie o servidor na porta 8000.')
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

function postJson<T>(caminho: string, corpo: RequisicaoCalculo | RequisicaoValidar, signal?: AbortSignal): Promise<T> {
  return requisitar<T>(caminho, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(corpo),
    signal,
  })
}

const caminhoFestival = (festivalId: string) => `/festivais/${encodeURIComponent(festivalId)}`

export type Objetivo = 'maximo-shows' | 'maxima-satisfacao'

export const api = {
  listarFestivais: (signal?: AbortSignal) => requisitar<FestivalResumo[]>('/festivais', { signal }),

  obterGrade: (festivalId: string, dia: number, signal?: AbortSignal) =>
    requisitar<GradeResponse>(`${caminhoFestival(festivalId)}/grade?dia=${dia}`, { signal }),

  urlMapa: (festivalId: string) => `${BASE_URL}${caminhoFestival(festivalId)}/mapa`,

  importar: (arquivo: File, festivalBase?: string) => {
    const dados = new FormData()
    dados.append('arquivo', arquivo)
    if (festivalBase) dados.append('festival_base', festivalBase)
    return requisitar<ImportarResponse>('/festivais/importar', { method: 'POST', body: dados })
  },

  roteiro: (objetivo: Objetivo, req: RequisicaoCalculo, signal?: AbortSignal) =>
    postJson<RoteiroResponse>(`/roteiro/${objetivo}`, req, signal),

  dimensionamento: (req: RequisicaoCalculo, signal?: AbortSignal) =>
    postJson<DimensionamentoResponse>('/dimensionamento', req, signal),

  comparativo: (req: RequisicaoCalculo, signal?: AbortSignal) =>
    postJson<ComparativoResponse>('/comparativo', req, signal),

  validar: (req: RequisicaoValidar, signal?: AbortSignal) => postJson<ValidarResponse>('/validar', req, signal),
}
