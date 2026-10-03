// Espelho dos contratos da API (backend/app/models/schemas.py).
// Tempos sempre em minutos desde 00:00 do dia de festival; antes de 06:00 soma 1440.

export type ModoDeslocamento = 'uniforme' | 'matricial'

export type Estrategia =
  | 'interval_scheduling_guloso'
  | 'weighted_interval_scheduling_dp'
  | 'dag_longest_path'
  | 'guloso_menor_fim'
  | 'dp_ponderado'
  | 'fifo'
  | 'spt'
  | 'maior_peso'

export type Heuristica = 'fifo' | 'spt' | 'maior_peso'

// Health
export interface HealthResponse {
  status: 'ok'
}

// Festivais
export interface FestivalResumo {
  id: string
  nome: string
  dias: number
  total_shows: number
}

// Grade
export interface Palco {
  codigo: string
  nome: string
  x: number
  y: number
}

export interface Show {
  id: string
  artista: string
  palco: string
  inicio: number
  fim: number
  peso: number
}

export interface GradeResponse {
  festival: string
  dia: number
  palcos: Palco[]
  shows: Show[]
}

// Importação de CSV
export type ImportarResponse = FestivalResumo

export interface ErroLinha {
  linha: number
  coluna: string
  mensagem: string
}

export interface ErroImportacaoResponse {
  detail: string
  erros: ErroLinha[]
}

// Requisição comum às rotas de cálculo
export type Pesos = Record<string, number>

export interface RequisicaoCalculo {
  festival_id: string
  dia: number
  modo_deslocamento?: ModoDeslocamento
  delta_uniforme?: number
  pesos?: Pesos
}

// Roteiro
export interface Deslocamento {
  de: string
  para: string
  palco_origem: string
  palco_destino: string
  custo_min: number
  folga_min: number
}

export interface RoteiroResponse {
  estrategia: Estrategia
  otimo_garantido: boolean
  roteiro: string[]
  total_shows: number
  peso_total: number
  deslocamentos: Deslocamento[]
  tempo_execucao_ms: number
}

// Dimensionamento
export interface FaixaSobreposicao {
  minuto: number
  simultaneos: number
}

export interface DimensionamentoResponse {
  palcos_minimos: number
  profundidade_maxima: number
  limite_inferior_atingido: boolean
  palcos_reais: number
  alocacao: Record<string, string[]>
  sobreposicao_por_faixa: FaixaSobreposicao[]
}

// Comparativo: gap = (peso ótimo - peso da heurística) / peso ótimo x 100
export interface InstanciaResumo {
  total_shows: number
  dia: number
  modo_deslocamento: ModoDeslocamento
}

export interface ResultadoEstrategia {
  estrategia: Estrategia
  otimo_garantido: boolean
  total_shows: number
  peso_total: number
  tempo_ms: number
}

export interface ComparativoResponse {
  instancia: InstanciaResumo
  resultados: ResultadoEstrategia[]
  gap_percentual: Partial<Record<Heuristica, number>>
}

// Erros padrão do FastAPI com detail em português
export interface ErroApi {
  detail: string
  erros?: ErroLinha[]
}
