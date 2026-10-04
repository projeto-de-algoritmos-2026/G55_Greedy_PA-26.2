import { useCallback, useEffect, useState } from 'react'
import type { Pesos } from '../types'

// Notas de preferência por festival e dia. Vivem na sessão do navegador, sem servidor.

function chave(festivalId: string, dia: number) {
  return `rotafest:notas:${festivalId}:${dia}`
}

function ler(festivalId: string, dia: number): Pesos {
  try {
    const bruto = sessionStorage.getItem(chave(festivalId, dia))
    const valor: unknown = bruto ? JSON.parse(bruto) : {}
    return typeof valor === 'object' && valor !== null ? (valor as Pesos) : {}
  } catch {
    return {}
  }
}

export function useNotas(festivalId: string, dia: number) {
  const atual = chave(festivalId, dia)
  // Notas de cada festival e dia visitados nesta sessão, lidas do sessionStorage sob demanda.
  const [porChave, setPorChave] = useState<Record<string, Pesos>>({})
  const notas = porChave[atual] ?? ler(festivalId, dia)

  useEffect(() => {
    const salvas = porChave[atual]
    if (!salvas) return
    try {
      sessionStorage.setItem(atual, JSON.stringify(salvas))
    } catch {
      // Sem sessionStorage (modo privado restrito), as notas ficam só em memória.
    }
  }, [atual, porChave])

  /** Nota 1 é o padrão do backend, então não precisa ser enviada. */
  const definir = useCallback(
    (showId: string, nota: number) => {
      setPorChave((estado) => {
        const proximas = { ...(estado[atual] ?? ler(festivalId, dia)) }
        if (nota <= 1) delete proximas[showId]
        else proximas[showId] = Math.min(10, Math.round(nota))
        return { ...estado, [atual]: proximas }
      })
    },
    [atual, festivalId, dia],
  )

  const limpar = useCallback(() => setPorChave((estado) => ({ ...estado, [atual]: {} })), [atual])

  return { notas, definir, limpar }
}
