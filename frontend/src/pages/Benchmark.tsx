import { Download, Play } from 'lucide-react'
import { useCallback, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Cabecalho } from '../components/Cabecalho'
import { Carregando, Erro } from '../components/Estados'
import { api } from '../services/api'
import type { BenchmarkResponse, PontoBenchmark } from '../types'

const CORES_ALGORITMOS: Record<string, string> = {
  interval_scheduling: 'var(--color-palco-3)',
  weighted_scheduling: 'var(--color-palco-1)',
  interval_partitioning: 'var(--color-palco-4)',
  dag_longest_path: 'var(--color-ipe)',
}

const NOMES_ALGORITMOS: Record<string, string> = {
  interval_scheduling: 'Interval Scheduling',
  weighted_scheduling: 'Weighted Scheduling DP',
  interval_partitioning: 'Interval Partitioning',
  dag_longest_path: 'Caminho Máximo DAG',
}

export function Benchmark() {
  const [params] = useSearchParams()
  const festivalId = params.get('festival') ?? ''
  
  const [rodando, setRodando] = useState(false)
  const [resultado, setResultado] = useState<BenchmarkResponse | null>(null)
  const [erro, setErro] = useState<Error | null>(null)

  const executarBenchmark = useCallback(async () => {
    setRodando(true)
    setErro(null)
    setResultado(null)
    try {
      // Usando o AbortController nativo caso o usuário saia da página seria o ideal,
      // mas vamos manter simples
      const res = await api.benchmark()
      setResultado(res)
    } catch (err) {
      setErro(err instanceof Error ? err : new Error(String(err)))
    } finally {
      setRodando(false)
    }
  }, [])

  const baixarCsv = useCallback(() => {
    if (!resultado) return
    const linhas = ['n,algoritmo,complexidade,tempo_ms_medio']
    for (const p of resultado.pontos) {
      linhas.push(`${p.n},${p.algoritmo},${p.complexidade},${p.tempo_ms_medio}`)
    }
    const blob = new Blob([linhas.join('\n')], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'benchmark_rotafest.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }, [resultado])

  return (
    <div className="flex min-h-screen flex-col">
      <Cabecalho>
        <div className="flex min-w-0 items-center gap-4">
          <h1 className="truncate font-display text-lg font-semibold text-texto-suave">
            Benchmark Algorítmico
          </h1>
        </div>
        <div className="ml-auto flex items-center gap-4">
          <Link to={festivalId ? `/planejador?${params.toString()}` : '/'} className="text-sm text-texto-suave hover:text-texto">
            Voltar
          </Link>
        </div>
      </Cabecalho>

      <main className="mx-auto flex w-full max-w-6xl flex-col gap-8 p-8">
        <section className="flex items-center justify-between rounded-xl border border-linha bg-superficie p-6">
          <div>
            <h2 className="font-display text-xl font-semibold">Desempenho Teórico vs Prático</h2>
            <p className="mt-1 text-sm text-texto-suave">
              Mede o tempo real de execução dos algoritmos para instâncias de tamanho N crescente. 
              Verifica o comportamento O(n log n) e O(n²).
            </p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={executarBenchmark}
              disabled={rodando}
              className="inline-flex items-center gap-2 rounded-lg bg-ipe px-4 py-2 font-bold text-noite transition-colors hover:bg-ipe/90 disabled:opacity-50"
            >
              <Play className="size-4" fill="currentColor" />
              {rodando ? 'Rodando...' : 'Rodar Benchmark'}
            </button>
            {resultado && (
              <button
                onClick={baixarCsv}
                className="inline-flex items-center gap-2 rounded-lg border border-linha px-4 py-2 font-medium text-texto transition-colors hover:bg-superficie-alta"
              >
                <Download className="size-4" />
                Exportar CSV
              </button>
            )}
          </div>
        </section>

        {rodando && (
          <div className="rounded-xl border border-linha bg-superficie p-12">
            <Carregando texto="Executando algoritmos... isso pode levar de 5 a 10 segundos para gerar instâncias de até 500 shows." />
          </div>
        )}
        
        {erro && !rodando && (
          <div className="rounded-xl border border-linha bg-superficie p-6">
            <Erro erro={erro as any} aoTentarDeNovo={executarBenchmark} />
          </div>
        )}

        {resultado && !rodando && (
          <>
            <section className="rounded-xl border border-linha bg-superficie p-6">
              <h2 className="mb-6 font-display text-xl font-semibold">Gráfico de Tempo de Execução</h2>
              
              <div className="relative h-96 w-full pr-4 pb-6 pt-4 pl-12 border-b border-l border-linha/50 mt-4">
                <span className="absolute -left-4 top-1/2 -translate-x-1/2 -rotate-90 text-xs text-texto-suave">Tempo (ms)</span>
                <span className="absolute bottom-1 left-1/2 -translate-x-1/2 text-xs text-texto-suave">N (número de shows)</span>
                
                {(() => {
                  const maxTime = Math.max(...resultado.pontos.map((p) => p.tempo_ms_medio), 0.1);
                  const maxN = Math.max(...resultado.ns);
                  
                  // Agrupar pontos por algoritmo
                  const series: Record<string, PontoBenchmark[]> = {};
                  for (const p of resultado.pontos) {
                    if (!series[p.algoritmo]) series[p.algoritmo] = [];
                    series[p.algoritmo]!.push(p);
                  }

                  return (
                    <>
                      {/* Eixo Y linhas */}
                      {[0, 0.25, 0.5, 0.75, 1].map((f) => (
                        <div key={f} className="absolute left-10 right-4 flex items-center border-b border-linha/30" style={{ bottom: `${f * 100}%`, height: 0 }}>
                          <span className="absolute -left-10 text-xs text-texto-suave">{(maxTime * f).toFixed(1)}</span>
                        </div>
                      ))}

                      {/* Eixo X labels */}
                      {resultado.ns.map((n) => (
                        <div key={n} className="absolute bottom-0 flex flex-col items-center" style={{ left: `calc(3rem + ${(n / maxN) * 100}%)`, transform: 'translateX(-50%)' }}>
                          <div className="h-1 w-px bg-linha/50"></div>
                          <span className="mt-1 text-xs text-texto-suave">{n}</span>
                        </div>
                      ))}
                      
                      {/* Desenhando linhas com div e clip-path (alternativa simples) ou pontinhos */}
                      {Object.entries(series).map(([algoritmo, pontos]) => {
                        return pontos.sort((a, b) => a.n - b.n).map((p, i, arr) => {
                          const x = (p.n / maxN) * 100;
                          const y = (p.tempo_ms_medio / maxTime) * 100;
                          
                          // Linha até o próximo ponto
                          let lineStyle = {};
                          if (i < arr.length - 1) {
                            const next = arr[i+1]!;
                            const nextX = (next.n / maxN) * 100;
                            const nextY = (next.tempo_ms_medio / maxTime) * 100;
                            const dx = nextX - x;
                            const dy = nextY - y;
                            const length = Math.sqrt(dx*dx + dy*dy);
                            const angle = Math.atan2(-dy, dx) * (180 / Math.PI);
                            
                            lineStyle = {
                              width: `${length}%`,
                              transform: `rotate(${angle}deg)`,
                              backgroundColor: CORES_ALGORITMOS[algoritmo],
                            };
                          }

                          return (
                            <div key={p.n} className="absolute bottom-0 left-0 h-full w-full pointer-events-none" style={{ left: '3rem', width: 'calc(100% - 4rem)' }}>
                              <div
                                className="absolute h-2 w-2 -translate-x-1/2 translate-y-1/2 rounded-full z-10 pointer-events-auto cursor-help group"
                                style={{ left: `${x}%`, bottom: `${y}%`, backgroundColor: CORES_ALGORITMOS[algoritmo] }}
                              >
                                <div className="absolute -top-8 left-1/2 hidden -translate-x-1/2 whitespace-nowrap rounded bg-superficie-alta px-2 py-1 text-xs text-texto shadow-lg group-hover:block z-20">
                                  {NOMES_ALGORITMOS[algoritmo]}: {p.tempo_ms_medio.toFixed(2)}ms (n={p.n})
                                </div>
                              </div>
                              {i < arr.length - 1 && (
                                <div 
                                  className="absolute h-0.5 origin-left"
                                  style={{ left: `${x}%`, bottom: `${y}%`, ...lineStyle }}
                                ></div>
                              )}
                            </div>
                          );
                        });
                      })}
                    </>
                  );
                })()}
              </div>
              
              <div className="mt-8 flex flex-wrap justify-center gap-6">
                {Object.keys(NOMES_ALGORITMOS).map((alg) => (
                  <div key={alg} className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full" style={{ backgroundColor: CORES_ALGORITMOS[alg] }}></div>
                    <span className="text-sm text-texto">{NOMES_ALGORITMOS[alg]}</span>
                    <span className="text-xs text-texto-suave">
                      ({alg === 'dag_longest_path' ? 'O(n²)' : 'O(n log n)'})
                    </span>
                  </div>
                ))}
              </div>
            </section>
            
            <section className="rounded-xl border border-linha bg-superficie p-6">
              <h2 className="mb-6 font-display text-xl font-semibold">Tabela de Dados ({resultado.repeticoes} repetições por ponto)</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="border-b border-linha text-texto-suave">
                    <tr>
                      <th className="pb-3 pr-4 font-medium">N Shows</th>
                      <th className="pb-3 px-4 font-medium">Algoritmo</th>
                      <th className="pb-3 px-4 font-medium">Complexidade</th>
                      <th className="pb-3 pl-4 font-medium text-right">Tempo Médio (ms)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-linha/50">
                    {resultado.pontos.sort((a, b) => a.n - b.n || a.algoritmo.localeCompare(b.algoritmo)).map((p) => (
                      <tr key={`${p.n}-${p.algoritmo}`} className="hover:bg-superficie-alta/50">
                        <td className="py-3 pr-4 font-mono">{p.n}</td>
                        <td className="py-3 px-4 text-texto">{NOMES_ALGORITMOS[p.algoritmo] || p.algoritmo}</td>
                        <td className="py-3 px-4 font-mono text-texto-suave">{p.complexidade}</td>
                        <td className="py-3 pl-4 text-right font-mono font-medium">{p.tempo_ms_medio.toFixed(3)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  )
}
