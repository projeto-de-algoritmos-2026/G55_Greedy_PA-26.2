import { defineConfig } from '@playwright/test'

// Roda contra o app já no ar (docker compose up ou npm run dev com o backend ligado).
export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: process.env.ROTAFEST_URL ?? 'http://localhost:5173',
    viewport: { width: 1366, height: 768 },
    deviceScaleFactor: 2,
    colorScheme: 'dark',
  },
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
})
