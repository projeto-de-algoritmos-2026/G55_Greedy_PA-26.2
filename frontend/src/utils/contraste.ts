// Razão de contraste WCAG 2.x entre duas cores hexadecimais.

function luminancia(hex: string): number {
  const canais = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
  const [r, g, b] = canais.map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)) as [number, number, number]
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

export function razaoContraste(a: string, b: string): number {
  const [maior, menor] = [luminancia(a), luminancia(b)].sort((x, y) => y - x) as [number, number]
  return (maior + 0.05) / (menor + 0.05)
}
