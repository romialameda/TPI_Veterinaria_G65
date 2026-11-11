import { useEffect, useState } from 'react'
import { api, fechaHora } from '../../api.js'

export default function Logistica() {
  const [muestras, setMuestras] = useState([])        // Muestras extraídas esperando ser empaquetadas
  const [remitos, setRemitos] = useState([])
  const [clinicas, setClinicas] = useState([])
  const [laboratorios, setLaboratorios] = useState([])
  const [conservadoras, setConservadoras] = useState([])
  const [nuevo, setNuevo] = useState({ id_clinica: '', id_laboratorio: '', numero_conservadora: '', codigos: [] })
  const [transportista, setTransportista] = useState({})  // { id_remito: texto }
  const [evento, setEvento] = useState({})                // { id_remito: { ubicacion, novedad, observacion } }
  const [novedades, setNovedades] = useState([])          // Opciones: Sin novedad, Demora, Golpe...
  const [mensaje, setMensaje] = useState('')

  async function cargar() {
    setMuestras(await api.get('/muestras?estado=' + encodeURIComponent('Extraída')))
    setRemitos(await api.get('/remitos'))
    setConservadoras(await api.get('/conservadoras'))
  }

  useEffect(() => {
    api.get('/clinicas').then(setClinicas)
    api.get('/laboratorios').then(setLaboratorios)
    api.get('/novedades-traslado').then(setNovedades)
    cargar()
  }, [])

  async function ejecutar(accion, texto) {
    try {
      await accion()
      setMensaje(texto)
      await cargar()
    } catch (err) {
      setMensaje('Error: ' + err.message)
    }
  }

  function marcarMuestra(codigo) {
    const codigos = nuevo.codigos.includes(codigo)
      ? nuevo.codigos.filter((c) => c !== codigo)
      : [...nuevo.codigos, codigo]
    setNuevo({ ...nuevo, codigos })
  }

  function armarRemito(e) {
    e.preventDefault()
    ejecutar(async () => {
      await api.post('/remitos', {
        id_clinica: Number(nuevo.id_clinica),
        id_laboratorio: Number(nuevo.id_laboratorio),
        numero_conservadora: Number(nuevo.numero_conservadora),
        codigos_muestras: nuevo.codigos,
      })
      setNuevo({ ...nuevo, numero_conservadora: '', codigos: [] })
    }, 'Remito armado y precinto generado.')
  }

  const muestrasDeLaClinica = muestras.filter((m) => String(m.id_clinica) === nuevo.id_clinica)
  const campo = (nombre) => ({ value: nuevo[nombre], onChange: (e) => setNuevo({ ...nuevo, [nombre]: e.target.value, codigos: [] }) })

  return (
    <>
      <h2>Logística de muestras</h2>
      {mensaje && <p className="mensaje">{mensaje}</p>}

      <form onSubmit={armarRemito} className="tarjeta">
        <h3>Armar remito (empaquetar muestras)</h3>
        <div className="fila">
          <label>Clínica de origen
            <select {...campo('id_clinica')} required>
              <option value="">Elegir...</option>
              {clinicas.map((c) => <option key={c.id_clinica} value={c.id_clinica}>{c.nombre}</option>)}
            </select>
          </label>
          <label>Laboratorio
            <select {...campo('id_laboratorio')} required>
              <option value="">Elegir...</option>
              {laboratorios.map((l) => <option key={l.id_laboratorio} value={l.id_laboratorio}>{l.nombre}</option>)}
            </select>
          </label>
          <label>Conservadora disponible
            <select value={nuevo.numero_conservadora} onChange={(e) => setNuevo({ ...nuevo, numero_conservadora: e.target.value })} required>
              <option value="">Elegir...</option>
              {conservadoras.map((c) => <option key={c.numero} value={c.numero}>#{c.numero} (hasta {c.capacidad_maxima} muestras)</option>)}
            </select>
          </label>
        </div>
        <p>Muestras extraídas en la clínica:</p>
        {!nuevo.id_clinica && <p className="ayuda">Elegí una clínica para ver sus muestras.</p>}
        {nuevo.id_clinica && muestrasDeLaClinica.length === 0 && <p className="ayuda">No hay muestras para empaquetar.</p>}
        {muestrasDeLaClinica.map((m) => (
          <label key={m.codigo} className="check">
            <input type="checkbox" checked={nuevo.codigos.includes(m.codigo)} onChange={() => marcarMuestra(m.codigo)} />
            {m.codigo} - {m.tipo} de {m.mascota} ({m.tipo_estudio})
          </label>
        ))}
        <button type="submit" disabled={nuevo.codigos.length === 0}>Armar remito</button>
      </form>

      <h3>Remitos</h3>
      {remitos.map((r) => (
        <div key={r.id_remito} className="tarjeta">
          <h4>Remito #{r.id_remito} <span className="estado">{r.estado}{r.con_observaciones ? ' con observaciones' : ''}</span></h4>
          <p>
            {r.clinica} → {r.laboratorio} | Conservadora #{r.conservadora} | Precinto {r.precinto.codigo}
            {r.transportista && <> | Transporte: {r.transportista}</>}
          </p>
          <p>Muestras: {r.muestras.map((m) => `${m.codigo} (${m.estado}${m.motivo_rechazo && m.estado === 'Rechazada' && r.con_observaciones ? ': ' + m.motivo_rechazo.split(': ').pop() : ''})`).join(', ')}</p>

          {r.estado === 'En preparación' && (
            <div className="fila">
              <input placeholder="Transportista" value={transportista[r.id_remito] || ''}
                onChange={(e) => setTransportista({ ...transportista, [r.id_remito]: e.target.value })} />
              <button disabled={!(transportista[r.id_remito] || '').trim()} onClick={() => ejecutar(() => api.post(`/remitos/${r.id_remito}/despachar`, { transportista: transportista[r.id_remito] || '' }), 'Remito despachado.')}>
                Despachar
              </button>
            </div>
          )}

          {r.eventos.length > 0 && (
            <ul>
              {r.eventos.map((ev, i) => (
                <li key={i}>
                  {fechaHora(ev.fecha_hora)} - {ev.ubicacion}:{' '}
                  <span className={ev.tiene_novedad ? 'alerta' : ''}>{ev.novedad}</span>
                  {ev.observacion && ` - ${ev.observacion}`}
                </li>
              ))}
            </ul>
          )}

          {r.estado === 'En tránsito' && (
            <div className="evento">
              <strong>Registrar evento del traslado</strong>
              <p className="ayuda">Lo que informa el transportista en cada punto del viaje. Las novedades le llegan al laboratorio al recibir el remito.</p>
              <div className="fila">
              <label>Ubicación
                <input placeholder="Ej: Ruta 9 km 15" value={evento[r.id_remito]?.ubicacion || ''}
                  onChange={(e) => setEvento({ ...evento, [r.id_remito]: { ...evento[r.id_remito], ubicacion: e.target.value } })} />
              </label>
              <label>Novedad
                <select value={evento[r.id_remito]?.novedad || 'Sin novedad'}
                  onChange={(e) => setEvento({ ...evento, [r.id_remito]: { ...evento[r.id_remito], novedad: e.target.value } })}>
                  {novedades.map((n) => <option key={n}>{n}</option>)}
                </select>
              </label>
              <label>Observación {evento[r.id_remito]?.novedad === 'Otro' ? '(obligatoria)' : '(opcional)'}
                <input placeholder="Ej: paso por control policial" value={evento[r.id_remito]?.observacion || ''}
                  onChange={(e) => setEvento({ ...evento, [r.id_remito]: { ...evento[r.id_remito], observacion: e.target.value } })} />
              </label>
              <button disabled={!(evento[r.id_remito]?.ubicacion || '').trim()
                || (evento[r.id_remito]?.novedad === 'Otro' && !(evento[r.id_remito]?.observacion || '').trim())}
                onClick={() => {
                  const ev = evento[r.id_remito] || {}
                  ejecutar(async () => {
                    await api.post(`/remitos/${r.id_remito}/eventos`, {
                      ubicacion: ev.ubicacion || '', novedad: ev.novedad || 'Sin novedad', observacion: ev.observacion || '',
                    })
                    setEvento({ ...evento, [r.id_remito]: {} })
                  }, 'Evento registrado.')
                }}>Registrar evento</button>
              </div>
            </div>
          )}

          {r.precinto.inspeccionado && (
            <p>Recepción {fechaHora(r.fecha_recepcion)}: precinto {r.precinto.intacto ? 'intacto' : `ROTO (${r.precinto.observaciones})`}</p>
          )}
        </div>
      ))}
    </>
  )
}
