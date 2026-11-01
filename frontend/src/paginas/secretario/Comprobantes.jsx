import { useEffect, useState } from 'react'
import { api, fechaHora, pesos } from '../../api.js'

export default function Comprobantes() {
  const [consultas, setConsultas] = useState([])
  const [comprobante, setComprobante] = useState(null)
  const [mensaje, setMensaje] = useState('')

  useEffect(() => { api.get('/consultas').then(setConsultas) }, [])

  async function emitir(id) {
    try {
      setComprobante(await api.post(`/consultas/${id}/comprobante`))
      setMensaje('')
    } catch (err) {
      setMensaje('Error: ' + err.message)
    }
  }

  return (
    <>
      <h2>Comprobantes de atención</h2>
      {mensaje && <p className="mensaje">{mensaje}</p>}

      {comprobante && (
        <div className="tarjeta comprobante">
          <h3>Comprobante #{comprobante.id_comprobante}</h3>
          <p>{fechaHora(comprobante.fecha)} - {comprobante.clinica}</p>
          <p>Cliente: {comprobante.cliente} | Paciente: {comprobante.mascota} | Atendió: {comprobante.veterinario}</p>
          <table>
            <tbody>
              {comprobante.items.map((i, n) => <tr key={n}><td>{i.descripcion}</td><td className="numero">{pesos(i.importe)}</td></tr>)}
              <tr><th>TOTAL</th><th className="numero">{pesos(comprobante.total)}</th></tr>
            </tbody>
          </table>
          <button onClick={() => setComprobante(null)}>Cerrar</button>
        </div>
      )}

      <table>
        <thead><tr><th>Fecha</th><th>Tipo</th><th>Mascota</th><th>Responsable</th><th>Veterinario</th><th>Costo</th><th></th></tr></thead>
        <tbody>
          {consultas.map((c) => (
            <tr key={c.id_consulta}>
              <td>{fechaHora(c.fecha_hora)}</td><td>{c.tipo_atencion}</td><td>{c.mascota}</td>
              <td>{c.responsable}</td><td>{c.veterinario}</td><td className="numero">{pesos(c.costo)}</td>
              <td><button onClick={() => emitir(c.id_consulta)}>Emitir comprobante</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  )
}
