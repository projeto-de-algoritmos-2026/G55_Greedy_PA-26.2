import { Link, useSearchParams } from 'react-router-dom'
import { Cabecalho } from '../components/Cabecalho'
import { Carregando, Erro, Vazio } from '../components/Estados'
import { api } from '../services/api'
import { useRequisicao } from '../services/useRequisicao'
import type { GradeResponse } from '../types'
import { mapearCoresPalcos } from '../utils/palcos'
import { formatarDuracao, minutosParaHHMM, viraDia } from '../utils/tempo'

// Marco do Dia 1 (SPEC 10): a grade real renderizada em lista simples.
// A grade visual por palco (GradeFestival) entra na T-603.
export function Planejador() {
  const [params] = useSearchParams()
  const festivalId = params.get('festival') ?? ''
  const dia = Math.max(1, Number(params.get('dia')) || 1)

  const estado = useRequisicao(() => api.obterGrade(festivalId, dia), [festivalId, dia])

  return (
    <>
      <Cabecalho>
        <Link to="/" className="text-sm text-texto-suave hover:text-texto">
          Trocar festival
        </Link>
      </Cabecalho>
      <main className="mx-auto max-w-6xl px-6 py-8">
        {!festivalId ? (
          <Vazio titulo="Nenhum festival selecionado" descricao="Volte à tela inicial e escolha um festival." />
        ) : estado.status === 'carregando' ? (
          <Carregando texto="Carregando grade…" />
        ) : estado.status === 'erro' ? (
          <Erro erro={estado.erro} />
        ) : estado.dados.shows.length === 0 ? (
          <Vazio titulo="Nenhum show neste dia" />
        ) : (
          <ListaGrade grade={estado.dados} />
        )}
      </main>
    </>
  )
}

function ListaGrade({ grade }: { grade: GradeResponse }) {
  const cores = mapearCoresPalcos(grade.palcos)
  const nomes = new Map(grade.palcos.map((p) => [p.codigo, p.nome]))

  return (
    <>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-texto-suave">Dia {grade.dia}</p>
          <h1 className="text-2xl font-semibold tracking-tight">{grade.festival}</h1>
        </div>
        <ul className="flex flex-wrap gap-4 text-sm" aria-label="Palcos">
          {grade.palcos.map((p) => (
            <li key={p.codigo} className="flex items-center gap-2">
              <span className={`size-3 rounded-sm ${cores.get(p.codigo)?.fundo}`} aria-hidden />
              {p.nome}
            </li>
          ))}
        </ul>
      </div>

      <table className="mt-6 w-full overflow-hidden rounded-xl border border-borda bg-superficie text-sm">
        <thead className="border-b border-borda text-left text-texto-suave">
          <tr>
            <th className="px-4 py-2.5 font-medium">Horário</th>
            <th className="px-4 py-2.5 font-medium">Artista</th>
            <th className="px-4 py-2.5 font-medium">Palco</th>
            <th className="px-4 py-2.5 text-right font-medium">Duração</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-borda">
          {grade.shows.map((s) => (
            <tr key={s.id}>
              <td className="horario whitespace-nowrap px-4 py-2.5">
                {minutosParaHHMM(s.inicio)}–{minutosParaHHMM(s.fim)}
                {viraDia(s.fim) && (
                  <span className="ml-1.5 text-xs text-texto-suave" title="Termina na madrugada do dia seguinte">
                    +1
                  </span>
                )}
              </td>
              <td className="px-4 py-2.5 font-medium">{s.artista}</td>
              <td className="px-4 py-2.5">
                <span className={`rounded px-2 py-0.5 text-xs font-medium text-white ${cores.get(s.palco)?.fundo}`}>
                  {nomes.get(s.palco) ?? s.palco}
                </span>
              </td>
              <td className="horario px-4 py-2.5 text-right text-texto-suave">{formatarDuracao(s.fim - s.inicio)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  )
}
