// Cor do céu de Brasília ao longo do dia de festival, interpolada por minuto.

const PARADAS: readonly (readonly [number, string])[] = [
  [14 * 60, '#e8a866'], // fim de tarde
  [17 * 60 + 30, '#d9707a'], // pôr do sol
  [18 * 60 + 30, '#6a5a9e'], // crepúsculo
  [20 * 60, '#2a3366'], // começo da noite
  [23 * 60, '#141c38'], // noite
]

function paraRgb(hex: string): [number, number, number] {
  return [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)) as [number, number, number]
}

function paraHex([r, g, b]: [number, number, number]): string {
  return `#${[r, g, b].map((c) => Math.round(c).toString(16).padStart(2, '0')).join('')}`
}

/** Cor do céu no minuto dado, com os extremos fixos antes da primeira e depois da última parada. */
export function corDoCeu(minuto: number): string {
  const primeira = PARADAS[0]!
  const ultima = PARADAS[PARADAS.length - 1]!
  if (minuto <= primeira[0]) return primeira[1]
  if (minuto >= ultima[0]) return ultima[1]
  const indice = PARADAS.findIndex(([m]) => m > minuto)
  const [m0, c0] = PARADAS[indice - 1]!
  const [m1, c1] = PARADAS[indice]!
  const t = (minuto - m0) / (m1 - m0)
  const [a, b] = [paraRgb(c0), paraRgb(c1)]
  return paraHex([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t])
}

/** Paradas de gradiente CSS entre `inicio` e `fim`, a cada `passo` minutos. */
export function gradienteDoCeu(inicio: number, fim: number, passo = 30): string {
  const paradas: string[] = []
  for (let m = inicio; m <= fim; m += passo) {
    paradas.push(`${corDoCeu(m)} ${(((m - inicio) / (fim - inicio)) * 100).toFixed(2)}%`)
  }
  return `linear-gradient(to bottom, ${paradas.join(', ')})`
}
