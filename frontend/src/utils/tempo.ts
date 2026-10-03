// Conversão entre minutos do dia de festival e HH:MM.
// O dia de festival vai de 06:00 às 05:59; minutos >= 1440 são madrugada do dia seguinte.

export const MINUTOS_DIA = 1440
const CORTE_DIA_FESTIVAL = 6 * 60

const pad = (n: number) => String(n).padStart(2, '0')

/** Formata minutos como HH:MM, sem indicar a virada de dia. */
export function minutosParaHHMM(minutos: number): string {
  const noDia = ((minutos % MINUTOS_DIA) + MINUTOS_DIA) % MINUTOS_DIA
  return `${pad(Math.floor(noDia / 60))}:${pad(noDia % 60)}`
}

/** True quando o horário cai na madrugada do dia seguinte. */
export function viraDia(minutos: number): boolean {
  return minutos >= MINUTOS_DIA
}

/** Converte HH:MM em minutos do dia de festival, somando 1440 aos horários antes de 06:00. */
export function hhmmParaMinutos(hora: string): number {
  const m = /^([01]\d|2[0-3]):([0-5]\d)$/.exec(hora.trim())
  if (!m) throw new Error(`Formato inválido '${hora}'; use HH:MM de 24 horas.`)
  const minutos = Number(m[1]) * 60 + Number(m[2])
  return minutos >= CORTE_DIA_FESTIVAL ? minutos : minutos + MINUTOS_DIA
}

/** Duração em formato curto: "50 min", "1h", "1h30". */
export function formatarDuracao(minutos: number): string {
  const h = Math.floor(minutos / 60)
  const m = minutos % 60
  if (h === 0) return `${m} min`
  return m === 0 ? `${h}h` : `${h}h${pad(m)}`
}
