import { useMemo } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Cabecalho } from '../components/Cabecalho'
import { Carregando, Erro, Vazio } from '../components/Estados'
import { api } from '../services/api'
import { useRequisicao } from '../services/useRequisicao'
import type { Estrategia, RequisicaoCalculo } from '../types'

const DELTA_PADRAO = 12

const NOMES_ESTRATEGIAS: Record<Estrategia, string> = {
  interval_scheduling_guloso: 'Guloso (Menor Fim)',
  weighted_interval_scheduling_dp: 'Programação Dinâmica',
  dag_longest_path: 'Caminho Máximo (DAG)',
  guloso_menor_fim: 'Guloso (Menor Fim)',
  dp_ponderado: 'Programação Dinâmica',
  fifo: 'FIFO (Menor Início)',
  spt: 'SPT (Menor Duração)',
  maior_peso: 'Maior Peso (Greedy)',
}

export function Comparativo() {
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
  const result = useRequisicao(() => api.comparativo(req), [req])

  if (!festivalId) {
    return (
      <div className="flex h-screen flex-col">
        <Cabecalho />
        <Vazio titulo="Nenhum festival escolhido" descricao="Volte para a tela inicial." />
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Cabecalho>
        <div className="flex min-w-0 items-center gap-4">
          <h1 className="truncate font-display text-lg font-semibold text-texto-suave">
            {grade.status === 'sucesso' ? grade.dados.festival : ''} - Comparativo de Estratégias
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

      <main className="mx-auto flex w-full max-w-6xl flex-col gap-8 p-8">
        {result.status === 'carregando' && <Carregando texto="Calculando comparativo..." />}
        {result.status === 'erro' && <Erro erro={result.erro} />}
        {result.status === 'sucesso' && (
          <>
            <section className="rounded-xl border border-linha bg-superficie p-6">
              <h2 className="mb-6 font-display text-xl font-semibold">Tabela de Resultados</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="border-b border-linha text-texto-suave">
                    <tr>
                      <th className="pb-3 pr-4 font-medium">Estratégia</th>
                      <th className="pb-3 px-4 font-medium text-right">Shows</th>
                      <th className="pb-3 px-4 font-medium text-right">Peso Total</th>
                      <th className="pb-3 px-4 font-medium text-right">Tempo (ms)</th>
                      <th className="pb-3 px-4 font-medium text-right">Gap (%)</th>
                      <th className="pb-3 pl-4 font-medium">Garantia de Ótimo</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-linha/50">
                    {result.dados.resultados.map((r) => {
                      const gap = r.estrategia in result.dados.gap_percentual 
                        ? result.dados.gap_percentual[r.estrategia as keyof typeof result.dados.gap_percentual] 
                        : undefined;
                      
                      return (
                        <tr key={r.estrategia} className="hover:bg-superficie-alta/50">
                          <td className="py-3 pr-4 font-medium">{NOMES_ESTRATEGIAS[r.estrategia] || r.estrategia}</td>
                          <td className="py-3 px-4 text-right font-mono">{r.total_shows}</td>
                          <td className="py-3 px-4 text-right font-mono font-bold">{r.peso_total}</td>
                          <td className="py-3 px-4 text-right font-mono text-texto-suave">{r.tempo_ms.toFixed(2)}</td>
                          <td className="py-3 px-4 text-right font-mono text-erro">{gap !== undefined ? `${gap}%` : '-'}</td>
                          <td className="py-3 pl-4">
                            {r.otimo_garantido ? (
                              <span className="inline-flex rounded-full bg-palco-4/20 px-2 py-0.5 text-xs font-semibold text-palco-4">Sim</span>
                            ) : (
                              <span className="inline-flex rounded-full bg-erro/20 px-2 py-0.5 text-xs font-semibold text-erro">Não</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="rounded-xl border border-linha bg-superficie p-6">
              <h2 className="mb-6 font-display text-xl font-semibold">Peso Total por Estratégia</h2>
              
              <div className="flex h-64 items-end gap-4 border-b border-l border-linha pl-2 pb-1 pr-2 pt-6">
                {(() => {
                  const maxPeso = Math.max(...result.dados.resultados.map((r) => r.peso_total), 1);
                  return result.dados.resultados.map((r) => {
                    const heightPercent = (r.peso_total / maxPeso) * 100;
                    return (
                      <div key={r.estrategia} className="group relative flex h-full flex-1 flex-col justify-end">
                        <div 
                          className={`w-full rounded-t-sm transition-all ${r.otimo_garantido ? 'bg-ipe' : 'bg-linha hover:bg-texto-suave'}`}
                          style={{ height: `${heightPercent}%` }}
                        >
                          <div className="absolute -top-8 left-1/2 -translate-x-1/2 whitespace-nowrap rounded bg-superficie-alta px-2 py-1 text-xs text-texto opacity-0 shadow-lg transition-opacity group-hover:opacity-100">
                            {r.peso_total} pontos
                          </div>
                        </div>
                        <div className="mt-2 text-center text-xs text-texto-suave truncate w-full transform -rotate-45 origin-top-left absolute -bottom-16">
                          {NOMES_ESTRATEGIAS[r.estrategia] || r.estrategia}
                        </div>
                      </div>
                    );
                  });
                })()}
              </div>
              <div className="mt-20 flex justify-center gap-6 text-sm text-texto-suave">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-ipe"></div>
                  <span>Solução Exata</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-linha"></div>
                  <span>Heurística</span>
                </div>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  )
}
