import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Planejador } from './pages/Planejador'
import { Selecao } from './pages/Selecao'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Selecao />} />
        <Route path="/planejador" element={<Planejador />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
