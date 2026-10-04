import { Star } from 'lucide-react'
import { useCallback, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { BadgeOtimalidade } from '../components/BadgeOtimalidade'
import { Cabecalho } from '../components/Cabecalho'
import { ControlesOtimizacao } from '../components/ControlesOtimizacao'
import { Carregando, Erro, Esqueleto, Vazio } from '../components/Estados'
import { GradeFestival } from '../components/GradeFestival'
import { MapaRota } from '../components/MapaRota'
import { PainelPreferencias } from '../components/PainelPreferencias'
import { TimelineRoteiro } from '../components/TimelineRoteiro'
import { api, type Objetivo } from '../services/api'
import { useNotas } from '../services/useNotas'
import { useRequisicao } from '../services/useRequisicao'
import { useRoteiro } from '../services/useRoteiro'
import type { GradeResponse, ModoDeslocamento, RequisicaoCalculo, RoteiroResponse, Show } from '../types'

const DELTA_PADRAO = 12

function lerParametros(params: URLSearchParams) {
  const objetivo: Objetivo = params.get('objetivo') === 'maxima-satisfacao' ? 'maxima-satisfacao' : 'maximo-shows'
  const modo: ModoDeslocamento = params.get('modo') === 'matricial' ? 'matricial' : 'uniforme'
  const delta = Number(params.get('delta') ?? DELTA_PADRAO)
  return {
    festivalId: params.get('festival') ?? '',
    dia: Math.max(1, Number(params.get('dia')) || 1),
    objetivo,
    modo,
    delta: Number.isFinite(delta) && delta >= 0 ? delta : DELTA_PADRAO,
  }
}

export function Planejador() {
  const [params, setParams] = useSearchParams()
  const { festivalId, dia, objetivo, modo, delta } = lerParametros(params)
  const atualizar = useCallback(
    (mudancas: Record<string, string>) =>
      setParams((atuais) => {
        const proximos = new URLSearchParams(atuais)
        Object.entries(mudancas).forEach(([k, v]) => proximos.set(k, v))
        return proximos
      }, { replace: true }),
    [setParams],
  )

  const festivais = useRequisicao(() => api.listarFestivais(), [])
  const grade = useRequisicao(() => api.obterGrade(festivalId, dia), [festivalId, dia])
  const { notas, definir, limpar } = useNotas(festivalId, dia)
  const [painelAberto, setPainelAberto] = useState(false)
  const [tentativa, setTentativa] = useState(0)

  const requisicao = useMemo<RequisicaoCalculo | null>(
    () =>
      festivalId && grade.status === 'sucesso'
        ? { festival_id: festivalId, dia, modo_deslocamento: modo, ...(modo === 'uniforme' ? { delta_uniforme: delta } : {}), pesos: notas }
        : null,
    [festivalId, dia, modo, delta, notas, grade.status],
  )
  const roteiro = useRoteiro(objetivo, requisicao, tentativa)

  const festival = festivais.status === 'sucesso' ? festivais.dados.find((f) => f.id === festivalId) : undefined
  const resultado: RoteiroResponse | undefined =
    roteiro.status === 'sucesso' ? roteiro.dados : roteiro.status === 'erro' ? undefined : roteiro.anterior

  if (!festivalId) {
    return (
      <div className="flex h-screen flex-col">
        <Cabecalho />
        <Vazio titulo="Nenhum festival escolhido" descricao="Volte para a tela inicial e escolha um festival para montar o roteiro." />
      </div>
    )
  }

  return (
    <div className="flex h-screen flex-col">
      <Cabecalho>
        <div className="flex min-w-0 items-center gap-4">
          <h1 className="truncate font-display text-lg font-semibold text-texto-suave">
            {grade.status === 'sucesso' ? grade.dados.festival : festival?.nome}
          </h1>
          {festival && festival.dias > 1 && (
            <div role="radiogroup" aria-label="Dia do festival" className="flex gap-1">
              {Array.from({ length: festival.dias }, (_, i) => i + 1).map((d) => (
                <button
                  key={d}
                  role="radio"
                  aria-checked={d === dia}
                  onClick={() => atualizar({ dia: String(d) })}
                  className={`rounded-full px-3 py-1 text-sm font-medium ${d === dia ? 'bg-texto text-noite' : 'text-texto-suave hover:text-texto'}`}
                >
                  Dia {d}
                </button>
              ))}
            </div>
          )}
        </div>
        <div className="ml-auto flex items-center gap-4">
          <Link to="/" className="text-sm text-texto-suave hover:text-texto">
            Trocar festival
          </Link>
          <button
            onClick={() => setPainelAberto(true)}
            className="inline-flex items-center gap-2 rounded-lg border border-linha px-3 py-1.5 text-sm font-medium hover:bg-superficie"
          >
            <Star className="size-4 text-ipe" aria-hidden />
            Minhas notas
            {Object.keys(notas).length > 0 && (
              <span className="horario rounded-full bg-ipe px-1.5 text-xs font-bold text-noite">{Object.keys(notas).length}</span>
            )}
          </button>
        </div>
      </Cabecalho>

      <div className="flex h-14 shrink-0 items-center gap-4 border-b border-linha px-6">
        <ControlesOtimizacao
          objetivo={objetivo}
          modo={modo}
          delta={delta}
          aoMudarObjetivo={(o) => atualizar({ objetivo: o })}
          aoMudarModo={(m) => atualizar({ modo: m })}
          aoMudarDelta={(d) => atualizar({ delta: String(d) })}
        />
        <div className="ml-auto flex items-center gap-4">
          {resultado ? (
            <>
              <p className="horario flex items-baseline gap-3 text-sm text-texto-suave">
                <span className="font-display text-base font-semibold text-texto">{resultado.total_shows} shows</span>
                <span>nota total {resultado.peso_total}</span>
                <span title="Tempo do algoritmo no servidor">
                  em {resultado.tempo_execucao_ms.toLocaleString('pt-BR', { maximumFractionDigits: 2 })} ms
                </span>
              </p>
              <BadgeOtimalidade
                otimo={resultado.otimo_garantido}
                estrategia={resultado.estrategia}
                recalculando={roteiro.status === 'sucesso' && roteiro.recalculando}
              />
            </>
          ) : (
            roteiro.status === 'carregando' && <Esqueleto className="h-7 w-64 rounded-full" />
          )}
        </div>
      </div>

      <main className="flex min-h-0 flex-1">
        <section className="min-w-0 flex-1 overflow-y-auto" aria-label="Grade do festival">
          {grade.status === 'carregando' && <GradeCarregando />}
          {grade.status === 'erro' && <Erro erro={grade.erro} />}
          {grade.status === 'sucesso' &&
            (grade.dados.shows.length === 0 ? (
              <Vazio titulo="Este dia não tem shows" descricao="Escolha outro dia no topo da tela." />
            ) : (
              <GradeFestival
                palcos={grade.dados.palcos}
                shows={grade.dados.shows}
                ordem={new Map(resultado?.roteiro.map((id, i) => [id, i + 1]) ?? [])}
                notas={notas}
                aoDefinirNota={definir}
              />
            ))}
        </section>

        <aside className="flex w-[400px] shrink-0 flex-col border-l border-linha" aria-label="Seu roteiro">
          <PainelRoteiro
            grade={grade.status === 'sucesso' ? grade.dados : undefined}
            festivalId={festivalId}
            roteiro={roteiro}
            resultado={resultado}
            aoTentarDeNovo={() => setTentativa((t) => t + 1)}
          />
        </aside>
      </main>

      {grade.status === 'sucesso' && (
        <PainelPreferencias
          aberto={painelAberto}
          shows={grade.dados.shows}
          palcos={grade.dados.palcos}
          notas={notas}
          aoDefinirNota={definir}
          aoLimpar={limpar}
          aoFechar={() => setPainelAberto(false)}
        />
      )}
    </div>
  )
}

function GradeCarregando() {
  return (
    <Carregando texto="Carregando a grade">
      <div className="grid grid-cols-[64px_repeat(4,1fr)] gap-2 p-4">
        <div />
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="space-y-3">
            <Esqueleto className="h-5 w-2/3" />
            <Esqueleto className="h-24" />
            <Esqueleto className="h-16" />
            <Esqueleto className="h-28" />
          </div>
        ))}
      </div>
    </Carregando>
  )
}

function PainelRoteiro({ grade, festivalId, roteiro, resultado, aoTentarDeNovo }: {
  grade: GradeResponse | undefined
  festivalId: string
  roteiro: ReturnType<typeof useRoteiro>
  resultado: RoteiroResponse | undefined
  aoTentarDeNovo: () => void
}) {
  if (roteiro.status === 'erro') return <Erro erro={roteiro.erro} aoTentarDeNovo={aoTentarDeNovo} />
  if (!grade || !resultado) {
    return (
      <Carregando texto="Calculando o roteiro">
        <div className="space-y-4 p-4">
          <Esqueleto className="aspect-[1000/625]" />
          <Esqueleto className="h-14" />
          <Esqueleto className="h-14" />
          <Esqueleto className="h-14" />
        </div>
      </Carregando>
    )
  }
  if (resultado.roteiro.length === 0) {
    return (
      <Vazio
        titulo="Nenhum show cabe no roteiro"
        descricao="Com esse tempo entre shows não dá para chegar a nenhum. Diminua os minutos ou use a distância real entre palcos."
      />
    )
  }

  const porId = new Map(grade.shows.map((s) => [s.id, s]))
  const shows = resultado.roteiro.map((id) => porId.get(id)).filter((s): s is Show => s !== undefined)
  return (
    <>
      <div className="p-4 pb-2">
        <MapaRota urlMapa={api.urlMapa(festivalId)} palcos={grade.palcos} roteiro={shows} />
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto px-5 py-3">
        <TimelineRoteiro roteiro={shows} deslocamentos={resultado.deslocamentos} palcos={grade.palcos} />
      </div>
    </>
  )
}
