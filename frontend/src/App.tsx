import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Planejador } from './pages/Planejador'
import { Selecao } from './pages/Selecao'
import { Dimensionamento } from './pages/Dimensionamento'
import { Comparativo } from './pages/Comparativo'
import { Benchmark } from './pages/Benchmark'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Selecao />} />
        <Route path="/planejador" element={<Planejador />} />
        <Route path="/dimensionamento" element={<Dimensionamento />} />
        <Route path="/comparativo" element={<Comparativo />} />
        <Route path="/benchmark" element={<Benchmark />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
