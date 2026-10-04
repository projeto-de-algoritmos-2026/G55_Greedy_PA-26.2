import { Upload } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, ApiError } from '../services/api'
import { Erro } from './Estados'

export function ImportarGrade() {
  const navigate = useNavigate()
  const [arrastando, setArrastando] = useState(false)
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState<ApiError | null>(null)

  async function enviar(arquivo: File | undefined) {
    if (!arquivo) return
    setEnviando(true)
    setErro(null)
    try {
      const festival = await api.importar(arquivo)
      navigate(`/planejador?festival=${encodeURIComponent(festival.id)}&dia=1`)
    } catch (e) {
      setErro(e instanceof ApiError ? e : new ApiError(0, String(e)))
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div>
      <label
        onDragOver={(e) => {
          e.preventDefault()
          setArrastando(true)
        }}
        onDragLeave={() => setArrastando(false)}
        onDrop={(e) => {
          e.preventDefault()
          setArrastando(false)
          void enviar(e.dataTransfer.files[0])
        }}
        className={`flex cursor-pointer items-center gap-3 rounded-xl border border-dashed px-5 py-3.5 transition-colors focus-within:outline-2 focus-within:outline-ipe ${
          arrastando ? 'border-ipe bg-ipe/10' : 'border-linha hover:border-texto-suave'
        }`}
      >
        <Upload className="size-5 text-texto-suave" aria-hidden />
        <span className="text-sm">
          <span className="font-medium">{enviando ? 'Enviando a grade…' : 'Usar minha própria grade'}</span>
          <span className="block text-texto-suave">Arraste um CSV aqui ou clique para escolher</span>
        </span>
        <input type="file" accept=".csv,text/csv" className="sr-only" disabled={enviando} onChange={(e) => void enviar(e.target.files?.[0])} />
      </label>
      <a href="/exemplo_grade.csv" download className="mt-2 inline-block text-sm text-texto-suave underline decoration-linha underline-offset-4 hover:text-texto">
        Baixar modelo de CSV
      </a>
      {erro && (
        <div className="mt-3 rounded-xl border border-erro/30 bg-erro/5">
          <Erro erro={erro} />
        </div>
      )}
    </div>
  )
}
