import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Cabecalho } from '../components/Cabecalho'
import { Carregando, Erro, Esqueleto, Vazio } from '../components/Estados'
import { ImportarGrade } from '../components/ImportarGrade'
import { PosterLineup } from '../components/PosterLineup'
import { api } from '../services/api'
import { useRequisicao } from '../services/useRequisicao'
import type { FestivalResumo } from '../types'

export function Selecao() {
  const festivais = useRequisicao(() => api.listarFestivais(), [])

  return (
    <div className="min-h-screen">
      <Cabecalho />
      <main className="mx-auto max-w-6xl px-10 pt-12 pb-16">
        {festivais.status === 'carregando' && (
          <Carregando texto="Carregando festivais">
            <Esqueleto className="h-16 w-2/3" />
            <Esqueleto className="mt-8 h-40" />
          </Carregando>
        )}
        {festivais.status === 'erro' && <Erro erro={festivais.erro} />}
        {festivais.status === 'sucesso' &&
          (festivais.dados.length === 0 ? (
            <>
              <Vazio titulo="Nenhum festival disponível" descricao="Envie a grade de um festival em CSV para começar." />
              <div className="max-w-md">
                <ImportarGrade />
              </div>
            </>
          ) : (
            <Festival festivais={festivais.dados} />
          ))}
      </main>
    </div>
  )
}

function Festival({ festivais }: { festivais: FestivalResumo[] }) {
  const navigate = useNavigate()
  const [festivalId, setFestivalId] = useState(festivais[0]!.id)
  const [dia, setDia] = useState(1)
  const festival = festivais.find((f) => f.id === festivalId) ?? festivais[0]!
  const grade = useRequisicao(() => api.obterGrade(festival.id, dia), [festival.id, dia])

  return (
    <>
      {festivais.length > 1 && (
        <div role="radiogroup" aria-label="Festival" className="mb-8 flex flex-wrap gap-2">
          {festivais.map((f) => (
            <button
              key={f.id}
              role="radio"
              aria-checked={f.id === festival.id}
              onClick={() => {
                setFestivalId(f.id)
                setDia(1)
              }}
              className={`rounded-full border px-3 py-1 text-sm ${f.id === festival.id ? 'border-texto text-texto' : 'border-linha text-texto-suave hover:text-texto'}`}
            >
              {f.nome}
            </button>
          ))}
        </div>
      )}

      <h1 className="font-display text-6xl font-extrabold tracking-tight">{festival.nome}</h1>
      <p className="mt-3 max-w-2xl text-lg text-texto-suave">
        {festival.total_shows} shows em {festival.dias} {festival.dias === 1 ? 'dia' : 'dias'}. Escolha o dia e veja o melhor roteiro para não perder nada.
      </p>

      {festival.dias > 1 && (
          <div role="radiogroup" aria-label="Dia do festival" className="mt-10 flex gap-2">
            {Array.from({ length: festival.dias }, (_, i) => i + 1).map((d) => (
              <button
                key={d}
                role="radio"
                aria-checked={d === dia}
                onClick={() => setDia(d)}
                className={`rounded-full px-5 py-2 font-display text-lg font-semibold transition-colors ${
                  d === dia ? 'bg-texto text-noite' : 'bg-superficie text-texto-suave hover:text-texto'
                }`}
              >
                Dia {d}
              </button>
            ))}
          </div>
      )}

      <section className="mt-6 min-h-40">
        {grade.status === 'carregando' && (
          <Carregando texto="Carregando o lineup">
            <div className="space-y-4">
              <Esqueleto className="h-14 w-5/6" />
              <Esqueleto className="h-9 w-4/6" />
              <Esqueleto className="h-6 w-full" />
            </div>
          </Carregando>
        )}
        {grade.status === 'erro' && <Erro erro={grade.erro} />}
        {grade.status === 'sucesso' && <PosterLineup shows={grade.dados.shows} palcos={grade.dados.palcos} />}
      </section>

      <div className="mt-10 flex flex-wrap items-start gap-6">
        <button
          onClick={() => navigate(`/planejador?festival=${encodeURIComponent(festival.id)}&dia=${dia}`)}
          className="rounded-xl bg-ipe px-6 py-3.5 font-display text-lg font-bold text-noite transition-transform hover:-translate-y-0.5"
        >
          Montar meu roteiro
        </button>
        <div className="w-96">
          <ImportarGrade />
        </div>
      </div>
    </>
  )
}
