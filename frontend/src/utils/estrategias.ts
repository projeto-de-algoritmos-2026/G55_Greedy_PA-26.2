import type { Estrategia } from '../types'

// Nome e explicação de cada estratégia em linguagem de quem vai ao festival.

export const ESTRATEGIAS: Record<Estrategia, { nome: string; explicacao: string }> = {
  interval_scheduling_guloso: {
    nome: 'Guloso por menor término',
    explicacao: 'Escolhe sempre o show que acaba primeiro e cabe na agenda. Com tempo fixo entre shows, isso é comprovadamente ótimo.',
  },
  weighted_interval_scheduling_dp: {
    nome: 'Programação dinâmica',
    explicacao: 'Testa, para cada show, se vale mais incluí-lo ou deixá-lo de fora, reaproveitando as melhores combinações anteriores.',
  },
  dag_longest_path: {
    nome: 'Caminho de maior valor',
    explicacao: 'Liga cada show aos que dá tempo de alcançar a pé e escolhe a sequência de maior valor. Exato para qualquer distância entre palcos.',
  },
  guloso_menor_fim: {
    nome: 'Guloso por menor término',
    explicacao: 'Escolhe sempre o show que acaba primeiro e cabe na agenda.',
  },
  dp_ponderado: {
    nome: 'Programação dinâmica',
    explicacao: 'Solução exata de maior satisfação com tempo fixo entre shows.',
  },
  fifo: { nome: 'Primeiro a começar', explicacao: 'Vai pegando o próximo show que começa, sem olhar adiante.' },
  spt: { nome: 'Mais curto primeiro', explicacao: 'Prefere os sets mais curtos para tentar encaixar mais shows.' },
  maior_peso: { nome: 'Maior nota primeiro', explicacao: 'Prefere os shows com nota mais alta, ignorando o que vem depois.' },
}
