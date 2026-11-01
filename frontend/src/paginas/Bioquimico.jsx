import { useEffect, useState } from 'react'
import { api, fechaHora } from '../api.js'

// Convierte el texto "Hematocrito: 45%" (una línea por parámetro) en { Hematocrito: "45%" }
function leerValores(texto) {
  const valores = {}
  for (const linea of texto.split('\n')) {
    const [parametro, ...resto] = linea.split(':')
    if (parametro.trim() && resto.length) valores[parametro.trim()] = resto.join(':').trim()
  }
  return valores
}

export default function Bioquimico({ usuario }) {
  const [remitos, setRemitos] = useState([])     // En tránsito: por recibir
  const [muestras, setMuestras] = useState([])   // Recibidas: por analizar
  const [inspeccion, setInspeccion] = useState({}) // { id_remito: { intacto, observaciones } }
  const [resultado, setResultado] = useState({})   // { codigo: { valores, observaciones } }
  const [mensaje, setMensaje] = useState('')

  async function cargar() {
    setRemitos(await api.get('/remitos?estado=' + encodeURIComponent('En tránsito')))
    setMuestras(await api.get('/muestras?estado=Recibida'))
  }

  useEffect(() => { cargar() }, [])

  async function ejecutar(accion, texto) {
    try {
      await accion()
      setMensaje(texto)
      await cargar()
    } catch (err) {
      setMensaje('Error: ' + err.message)
    }
  }

  function recibir(r) {
    const datos = inspeccion[r.id_remito] || { intacto: true, observaciones: '' }
    ejecutar(() => api.post(`/remitos/${r.id_remito}/recibir`, {
      matricula_bioquimico: usuario.matricula,
      precinto_intacto: datos.intacto,
      observaciones: datos.observaciones,
    }), datos.intacto ? 'Remito recibido.' : 'Remito recibido con precinto roto: sus muestras quedaron rechazadas.')
  }

  function cargarResultado(m) {
    const datos = resultado[m.codigo] || { valores: '', observaciones: '' }
    ejecutar(() => api.post(`/muestras/${m.codigo}/resultado`, {
      matricula_bioquimico: usuario.matricula,
      valores: leerValores(datos.valores),
      observaciones: datos.observaciones,
    }), 'Resultado cargado.')
  }

  return (
    <>
      <h2>Laboratorio - {usuario.nombre}</h2>
      {mensaje && <p className="mensaje">{mensaje}</p>}

      <h3>Remitos por recibir</h3>
      {remitos.length === 0 && <p>No hay remitos en tránsito.</p>}
      {remitos.map((r) => {
        const datos = inspeccion[r.id_remito] || { intacto: true, observaciones: '' }
        return (
          <div key={r.id_remito} className="tarjeta">
            <h4>Remito #{r.id_remito} desde {r.clinica}</h4>
            <p>Despachado {fechaHora(r.fecha_despacho)} | {r.transportista} | Precinto {r.precinto.codigo}</p>
            <p>Muestras: {r.muestras.map((m) => `${m.codigo} (${m.tipo})`).join(', ')}</p>
            <div className="fila">
              <label className="check">
                <input type="radio" checked={datos.intacto} onChange={() => setInspeccion({ ...inspeccion, [r.id_remito]: { ...datos, intacto: true } })} />
                Precinto intacto
              </label>
              <label className="check">
                <input type="radio" checked={!datos.intacto} onChange={() => setInspeccion({ ...inspeccion, [r.id_remito]: { ...datos, intacto: false } })} />
                Precinto roto
              </label>
              <input placeholder="Observaciones" value={datos.observaciones}
                onChange={(e) => setInspeccion({ ...inspeccion, [r.id_remito]: { ...datos, observaciones: e.target.value } })} />
              <button onClick={() => recibir(r)}>Registrar recepción</button>
            </div>
          </div>
        )
      })}

      <h3>Muestras para analizar</h3>
      {muestras.length === 0 && <p>No hay muestras recibidas pendientes.</p>}
      {muestras.map((m) => {
        const datos = resultado[m.codigo] || { valores: '', observaciones: '' }
        return (
          <div key={m.codigo} className="tarjeta">
            <h4>{m.codigo} - {m.tipo}</h4>
            <p>Estudio: {m.tipo_estudio} | Paciente: {m.mascota} | {m.clinica}</p>
            <label>Valores (uno por línea, formato "Parámetro: valor")
              <textarea rows="3" value={datos.valores} placeholder={'Hematocrito: 45%\nLeucocitos: 12000'}
                onChange={(e) => setResultado({ ...resultado, [m.codigo]: { ...datos, valores: e.target.value } })} />
            </label>
            <label>Observaciones
              <input value={datos.observaciones} onChange={(e) => setResultado({ ...resultado, [m.codigo]: { ...datos, observaciones: e.target.value } })} />
            </label>
            <button onClick={() => cargarResultado(m)}>Cargar resultado</button>
          </div>
        )
      })}
    </>
  )
}
