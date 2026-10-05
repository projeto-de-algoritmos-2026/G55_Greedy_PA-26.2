import { useMemo } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Cabecalho } from '../components/Cabecalho'
import { Carregando, Erro, Vazio } from '../components/Estados'
import { api } from '../services/api'
import { useRequisicao } from '../services/useRequisicao'
import type { RequisicaoCalculo } from '../types'

const DELTA_PADRAO = 12

function formatarHorario(minutosDesdeMeiaNoite: number) {
  let m = minutosDesdeMeiaNoite
  if (m >= 1440) m -= 1440
  const horas = Math.floor(m / 60)
  const minutos = m % 60
  return `${horas.toString().padStart(2, '0')}:${minutos.toString().padStart(2, '0')}`
}

export function Dimensionamento() {
  const [params] = useSearchParams()
  const festivalId = params.get('festival') ?? ''
  const dia = Math.max(1, Number(params.get('dia')) || 1)
  const modo = params.get('modo') === 'matricial' ? 'matricial' : 'uniforme'
  const deltaParam = Number(params.get('delta') ?? DELTA_PADRAO)
  const delta = Number.isFinite(deltaParam) && deltaParam >= 0 ? deltaParam : DELTA_PADRAO

  const req = useMemo<RequisicaoCalculo>(
    () => ({ festival_id: festivalId, dia, modo_deslocamento: modo, ...(modo === 'uniforme' ? { delta_uniforme: delta } : {}) }),
    [festivalId, dia, modo, delta]
  )

  const grade = useRequisicao(() => api.obterGrade(festivalId, dia), [festivalId, dia])
  const result = useRequisicao(() => api.dimensionamento(req), [req])

  if (!festivalId) {
    return (
      <div className="flex h-screen flex-col">
        <Cabecalho />
        <Vazio titulo="Nenhum festival escolhido" descricao="Volte para a tela inicial." />
      </div>
    )
  }

  const suficiente = result.status === 'sucesso' && result.dados.palcos_reais >= result.dados.palcos_minimos

  return (
    <div className="flex min-h-screen flex-col">
      <Cabecalho>
        <div className="flex min-w-0 items-center gap-4">
          <h1 className="truncate font-display text-lg font-semibold text-texto-suave">
            {grade.status === 'sucesso' ? grade.dados.festival : ''} - Dimensionamento
          </h1>
          <div className="rounded-full bg-superficie px-3 py-1 text-sm font-medium text-texto-suave">
            Dia {dia}
          </div>
        </div>
        <div className="ml-auto flex items-center gap-4">
          <Link to={`/planejador?${params.toString()}`} className="text-sm text-texto-suave hover:text-texto">
            Voltar ao Planejador
          </Link>
        </div>
      </Cabecalho>

      <main className="mx-auto flex w-full max-w-5xl flex-col gap-8 p-8">
        {result.status === 'carregando' && <Carregando texto="Calculando dimensionamento..." />}
        {result.status === 'erro' && <Erro erro={result.erro} />}
        {result.status === 'sucesso' && (
          <>
            <section className="grid grid-cols-1 gap-6 md:grid-cols-3">
              <div className="flex flex-col rounded-xl border border-linha bg-superficie p-6">
                <span className="text-sm font-medium text-texto-suave">Palcos Necessários (Mínimo)</span>
                <span className="mt-2 font-display text-5xl font-bold text-texto">{result.dados.palcos_minimos}</span>
                <span className="mt-2 text-sm text-texto-suave">Interval Partitioning lower bound</span>
              </div>
              <div className="flex flex-col rounded-xl border border-linha bg-superficie p-6">
                <span className="text-sm font-medium text-texto-suave">Palcos Reais da Instância</span>
                <span className="mt-2 font-display text-5xl font-bold text-texto">{result.dados.palcos_reais}</span>
                <span className="mt-2 text-sm text-texto-suave">Presentes na grade</span>
              </div>
              <div className={`flex flex-col justify-center rounded-xl p-6 ${suficiente ? 'bg-palco-4/20 text-palco-4' : 'bg-erro/20 text-erro'}`}>
                <span className="font-display text-2xl font-bold">
                  {suficiente ? 'Capacidade Suficiente' : 'Faltam Palcos!'}
                </span>
                <span className="mt-2 text-sm opacity-90">
                  {suficiente
                    ? 'O festival tem palcos suficientes para acomodar os shows sem sobreposição indesejada nas salas virtuais.'
                    : `Seriam necessários ${result.dados.palcos_minimos - result.dados.palcos_reais} palcos adicionais para evitar colisão absoluta.`}
                </span>
              </div>
            </section>

            <section className="rounded-xl border border-linha bg-superficie p-6">
              <h2 className="mb-6 font-display text-xl font-semibold">Sobreposição Temporal (Profundidade Máxima: {result.dados.profundidade_maxima})</h2>
              
              <div className="relative h-64 w-full">
                {/* Y-axis lines */}
                {Array.from({ length: result.dados.profundidade_maxima + 1 }).map((_, i) => (
                  <div key={i} className="absolute left-0 right-0 flex items-end border-b border-linha/50 text-xs text-texto-suave" style={{ bottom: `${(i / result.dados.profundidade_maxima) * 100}%`, height: 0 }}>
                    <span className="absolute -left-6 bottom-[-8px]">{i}</span>
                  </div>
                ))}
                
                {/* Bars */}
                <div className="absolute inset-0 ml-2 flex items-end border-l border-linha/50 pl-2 pb-[1px]">
                  {(() => {
                    const series = result.dados.sobreposicao_por_faixa;
                    if (series.length === 0) return null;
                    
                    const minTime = series[0]!.minuto;
                    const maxTime = series[series.length - 1]!.minuto;
                    const duration = maxTime - minTime;
                    
                    if (duration === 0) return null;

                    return series.map((ponto, i) => {
                      if (i === series.length - 1) return null;
                      const nextPonto = series[i + 1]!;
                      
                      const widthPercent = ((nextPonto.minuto - ponto.minuto) / duration) * 100;
                      const heightPercent = (ponto.simultaneos / result.dados.profundidade_maxima) * 100;
                      
                      const isPico = ponto.simultaneos === result.dados.profundidade_maxima;

                      return (
                        <div
                          key={ponto.minuto}
                          className={`group relative h-full ${isPico ? 'bg-ipe' : 'bg-palco-3'}`}
                          style={{
                            width: `${widthPercent}%`,
                            height: `${heightPercent}%`,
                          }}
                        >
                          <div className="absolute -top-8 left-1/2 hidden -translate-x-1/2 whitespace-nowrap rounded bg-superficie-alta px-2 py-1 text-xs text-texto shadow-lg group-hover:block z-10">
                            {formatarHorario(ponto.minuto)} - {formatarHorario(nextPonto.minuto)}: {ponto.simultaneos} shows
                          </div>
                        </div>
                      );
                    });
                  })()}
                </div>
              </div>
              <div className="mt-4 text-center text-sm text-texto-suave">Tempo (início ao fim do festival)</div>
            </section>
          </>
        )}
      </main>
    </div>
  )
}
