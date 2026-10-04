import { expect, test, type Page } from '@playwright/test'
import path from 'node:path'

// Capturas de tela da interface em 1366×768, salvas em docs/img, e verificações de usabilidade.

const IMG = path.resolve(import.meta.dirname, '../../docs/img')
const PLANEJADOR = '/planejador?festival=festival-exemplo&dia=1'

async function esperarRoteiro(page: Page) {
  await expect(page.getByRole('list', { name: 'Roteiro em ordem cronológica' })).toBeVisible()
  await expect(page.getByText('Ótimo garantido')).toBeVisible()
  // Deixa a animação da rota terminar antes da captura.
  await page.waitForTimeout(800)
}

test('tela inicial com o lineup', async ({ page }) => {
  // Grades importadas por outros testes ficam na memória do backend; a captura mostra só o festival real.
  await page.route('**/api/festivais', async (rota) => {
    const resposta = await rota.fetch()
    const festivais = (await resposta.json()) as { id: string }[]
    await rota.fulfill({ response: resposta, json: festivais.filter((f) => !f.id.startsWith('upload-')) })
  })
  await page.goto('/')
  await expect(page.getByLabel('Lineup do dia')).toBeVisible()
  await page.screenshot({ path: `${IMG}/selecao.png` })
})

test('planejador com tempo fixo entre shows', async ({ page }) => {
  await page.goto(PLANEJADOR)
  await esperarRoteiro(page)
  await page.screenshot({ path: `${IMG}/grade.png` })
  await page.getByRole('complementary', { name: 'Seu roteiro' }).screenshot({ path: `${IMG}/mapa.png` })
})

test('planejador com distância real e notas', async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem('rotafest:notas:festival-exemplo:1', JSON.stringify({ S023: 10, S013: 8, S026: 7, S002: 6 }))
  })
  await page.goto(`${PLANEJADOR}&objetivo=maxima-satisfacao&modo=matricial`)
  await esperarRoteiro(page)
  await page.screenshot({ path: `${IMG}/planejador-satisfacao.png` })
  await page.getByRole('button', { name: /Minhas notas/ }).click()
  await expect(page.getByRole('dialog', { name: 'Minhas notas' })).toBeVisible()
  await page.screenshot({ path: `${IMG}/notas.png` })
})

test('estado vazio do roteiro', async ({ page }) => {
  await page.route('**/api/roteiro/**', (rota) =>
    rota.fulfill({
      json: {
        estrategia: 'interval_scheduling_guloso',
        otimo_garantido: true,
        roteiro: [],
        total_shows: 0,
        peso_total: 0,
        deslocamentos: [],
        tempo_execucao_ms: 0.1,
      },
    }),
  )
  await page.goto(PLANEJADOR)
  await expect(page.getByText('Nenhum show cabe no roteiro')).toBeVisible()
  await page.screenshot({ path: `${IMG}/estado-vazio.png` })
})

test('estado de erro mostra a mensagem do backend', async ({ page }) => {
  const detalhe = 'Pesos para shows que não existem no dia 1: S999.'
  await page.route('**/api/roteiro/**', (rota) => rota.fulfill({ status: 422, json: { detail: detalhe } }))
  await page.goto(PLANEJADOR)
  await expect(page.getByRole('alert')).toContainText(detalhe)
  await expect(page.getByRole('button', { name: 'Tentar de novo' })).toBeVisible()
  await page.screenshot({ path: `${IMG}/estado-erro.png` })
})

test('mudar uma nota recalcula o roteiro em menos de 500 ms', async ({ page }) => {
  await page.goto(`${PLANEJADOR}&objetivo=maxima-satisfacao`)
  await esperarRoteiro(page)
  const bloco = page.getByRole('button', { name: /^Os Últimos Ônibus,/ })
  await expect(bloco).toHaveAccessibleName(/fora do roteiro/)
  await bloco.focus()

  const inicio = Date.now()
  await page.keyboard.press('0')
  await expect(bloco).toHaveAccessibleName(/número \d+ do roteiro/, { timeout: 2000 })
  const decorrido = Date.now() - inicio
  console.log(`recálculo após mudar a nota: ${decorrido} ms`)
  expect(decorrido).toBeLessThan(500)
})

test('grade de 60 shows cabe em 1366 px sem rolagem horizontal', async ({ page, request }) => {
  const palcos = ['P1', 'P2', 'P3', 'P4']
  const linhas = ['id,artista,palco,dia,hora_inicio,hora_fim']
  for (let i = 0; i < 60; i++) {
    const inicio = 14 * 60 + Math.floor(i / 4) * 50 + (i % 4) * 10
    const fim = inicio + 45
    const hhmm = (m: number) => `${String(Math.floor(m / 60) % 24).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`
    linhas.push(`S${String(i + 1).padStart(3, '0')},Artista com nome bem comprido ${i + 1},${palcos[i % 4]},1,${hhmm(inicio)},${hhmm(fim)}`)
  }
  const resposta = await request.post('/api/festivais/importar', {
    multipart: { arquivo: { name: 'grade60.csv', mimeType: 'text/csv', buffer: Buffer.from(linhas.join('\n')) } },
  })
  expect(resposta.status()).toBe(201)
  const { id, total_shows } = (await resposta.json()) as { id: string; total_shows: number }
  expect(total_shows).toBe(60)

  await page.goto(`/planejador?festival=${id}&dia=1`)
  await esperarRoteiro(page)
  const larguras = await page.evaluate(() => ({
    documento: document.documentElement.scrollWidth,
    janela: window.innerWidth,
    grade: (() => {
      const g = document.querySelector('[aria-label="Grade do festival"]')
      return g ? g.scrollWidth - g.clientWidth : -1
    })(),
  }))
  expect(larguras.documento).toBeLessThanOrEqual(larguras.janela)
  expect(larguras.grade).toBe(0)
})
