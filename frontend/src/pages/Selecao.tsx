import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Cabecalho } from '../components/Cabecalho'
import { Carregando, Erro, Vazio } from '../components/Estados'
import { api } from '../services/api'
import { useRequisicao } from '../services/useRequisicao'
import type { FestivalResumo } from '../types'

export function Selecao() {
  const estado = useRequisicao(api.listarFestivais, [])

  return (
    <>
      <Cabecalho />
      <main className="mx-auto max-w-3xl px-6 py-12">
        <h1 className="text-3xl font-semibold tracking-tight">Monte seu roteiro de festival</h1>
        <p className="mt-2 max-w-xl text-texto-suave">
          Escolha o festival e o dia. O RotaFest calcula quais shows você consegue ver por completo,
          considerando o tempo de caminhada entre os palcos.
        </p>

        <section className="mt-10">
          {estado.status === 'carregando' && <Carregando texto="Buscando festivais…" />}
          {estado.status === 'erro' && <Erro erro={estado.erro} />}
          {estado.status === 'sucesso' &&
            (estado.dados.length === 0 ? (
              <Vazio titulo="Nenhum festival disponível" descricao="Adicione um diretório em backend/app/data." />
            ) : (
              <ListaFestivais festivais={estado.dados} />
            ))}
        </section>
      </main>
    </>
  )
}

function ListaFestivais({ festivais }: { festivais: FestivalResumo[] }) {
  const navigate = useNavigate()
  const [dias, setDias] = useState<Record<string, number>>({})

  return (
    <ul className="space-y-4">
      {festivais.map((f) => {
        const dia = dias[f.id] ?? 1
        return (
          <li key={f.id} className="rounded-xl border border-borda bg-superficie p-5">
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold">{f.nome}</h2>
                <p className="text-sm text-texto-suave">
                  {f.dias} {f.dias === 1 ? 'dia' : 'dias'} · {f.total_shows} shows
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div role="radiogroup" aria-label={`Dia do ${f.nome}`} className="flex rounded-lg border border-borda p-0.5">
                  {Array.from({ length: f.dias }, (_, i) => i + 1).map((d) => (
                    <button
                      key={d}
                      role="radio"
                      aria-checked={d === dia}
                      onClick={() => setDias({ ...dias, [f.id]: d })}
                      className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                        d === dia ? 'bg-texto text-fundo' : 'text-texto-suave hover:text-texto'
                      }`}
                    >
                      Dia {d}
                    </button>
                  ))}
                </div>
                <button
                  onClick={() => navigate(`/planejador?festival=${encodeURIComponent(f.id)}&dia=${dia}`)}
                  className="rounded-lg bg-palco-1 px-4 py-2 text-sm font-medium text-white hover:opacity-90"
                >
                  Planejar
                </button>
              </div>
            </div>
          </li>
        )
      })}
    </ul>
  )
}
