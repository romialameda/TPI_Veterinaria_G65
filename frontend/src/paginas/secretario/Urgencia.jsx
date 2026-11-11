import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, fechaHora, hoy, pesos } from '../../api.js'

const URGENCIA_VACIA = { id_mascota: '', matricula_veterinario: '', motivo: '' }

// Recepción registra la urgencia (sin turno). El veterinario la ve en "Urgencias de hoy" y la atiende.
export default function Urgencia({ mascotas, veterinarios }) {
  const navegar = useNavigate()
  const [urgencia, setUrgencia] = useState(URGENCIA_VACIA)
  const [precio, setPrecio] = useState(null)
  const [urgenciasHoy, setUrgenciasHoy] = useState([])
  const [mensaje, setMensaje] = useState('')

  async function cargarUrgencias() {
    const consultas = await api.get('/consultas')
    setUrgenciasHoy(consultas.filter((c) => c.tipo_atencion === 'Urgencia' && c.fecha_hora.slice(0, 10) === hoy()))
  }

  useEffect(() => {
    api.get('/tarifas').then((t) => setPrecio(t.atenciones.Urgencia))
    cargarUrgencias()
  }, [])

  async function registrar(e) {
    e.preventDefault()
    try {
      const c = await api.post('/consultas/urgencia', { ...urgencia, id_mascota: Number(urgencia.id_mascota) })
      setMensaje(`Urgencia registrada: ${c.mascota} ya figura en la lista de ${c.veterinario}.`)
      setUrgencia(URGENCIA_VACIA)
      cargarUrgencias()
    } catch (err) {
      setMensaje('Error: ' + err.message)
    }
  }

  return (
    <form onSubmit={registrar} className="tarjeta urgencia">
      <h3>Urgencia (sin turno)</h3>
      {mensaje && <p className="mensaje">{mensaje}</p>}
      <label>Mascota
        <select value={urgencia.id_mascota} required
          onChange={(e) => (e.target.value === 'registrar' ? navegar('/secretario/clientes') : setUrgencia({ ...urgencia, id_mascota: e.target.value }))}>
          <option value="">Elegir...</option>
          {mascotas.map((m) => <option key={m.id_mascota} value={m.id_mascota}>{m.nombre} ({m.especie}) - {m.responsable}</option>)}
          <option value="registrar">➕ Mascota no registrada (ir a registrarla)</option>
        </select>
      </label>
      <label>Veterinario que la atiende
        <select value={urgencia.matricula_veterinario} required onChange={(e) => setUrgencia({ ...urgencia, matricula_veterinario: e.target.value })}>
          <option value="">Elegir...</option>
          {veterinarios.map((v) => <option key={v.matricula} value={v.matricula}>{v.nombre_completo} - {v.clinica} - {v.horario}</option>)}
        </select>
      </label>
      <label>Motivo <input value={urgencia.motivo} required maxLength={200} onChange={(e) => setUrgencia({ ...urgencia, motivo: e.target.value })} /></label>
      {precio != null && <p className="precio">Precio de la urgencia: <strong>{pesos(precio)}</strong></p>}
      <button type="submit">Registrar urgencia</button>

      {urgenciasHoy.length > 0 && (
        <>
          <h4>Urgencias de hoy</h4>
          <ul>
            {urgenciasHoy.map((c) => (
              <li key={c.id_consulta}>{fechaHora(c.fecha_hora).slice(11)} - {c.mascota} con {c.veterinario} ({c.clinica}): {c.motivo}</li>
            ))}
          </ul>
        </>
      )}
    </form>
  )
}
