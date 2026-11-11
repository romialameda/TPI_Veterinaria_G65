import { useEffect, useState } from 'react'
import { api, fechaHora } from '../api.js'

const INSPECCION_INICIAL = { intacto: true, observaciones: '', rechazos: {} }  // rechazos: { codigo: { motivo, observacion } }

export default function Bioquimico({ usuario }) {
  const [remitos, setRemitos] = useState([])        // En tránsito: por recibir
  const [muestras, setMuestras] = useState([])      // Recibidas: por analizar
  const [motivos, setMotivos] = useState([])        // Motivos de rechazo de una muestra
  const [inspeccion, setInspeccion] = useState({})  // { id_remito: { intacto, observaciones, rechazos } }
  const [resultado, setResultado] = useState({})    // { codigo: texto del resultado }
  const [rechazo, setRechazo] = useState({})        // { codigo: { motivo, observacion } } para muestras ya recibidas
  const [mensaje, setMensaje] = useState('')

  async function cargar() {
    setRemitos(await api.get('/remitos?estado=' + encodeURIComponent('En tránsito')))
    setMuestras(await api.get('/muestras?estado=Recibida'))
  }

  useEffect(() => {
    api.get('/motivos-rechazo').then(setMotivos)
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

  function recibir(r) {
    const datos = inspeccion[r.id_remito] || INSPECCION_INICIAL
    const rechazos = datos.intacto
      ? Object.entries(datos.rechazos).map(([codigo, x]) => ({ codigo, motivo: x.motivo, observacion: x.observacion || '' }))
      : []
    const texto = !datos.intacto
      ? 'Remito recibido con precinto roto: se rechazaron todas sus muestras.'
      : rechazos.length ? `Remito recibido con observaciones: se rechazaron ${rechazos.length} muestra(s).` : 'Remito recibido.'
    ejecutar(() => api.post(`/remitos/${r.id_remito}/recibir`, {
      matricula_bioquimico: usuario.matricula, precinto_intacto: datos.intacto,
      observaciones: datos.observaciones, rechazos,
    }), texto)
  }

  // Marca o desmarca una muestra puntual como rechazada al recibir
  function marcarRechazo(r, codigo, marcada) {
    const datos = inspeccion[r.id_remito] || INSPECCION_INICIAL
    const rechazos = { ...datos.rechazos }
    if (marcada) rechazos[codigo] = { motivo: motivos[0], observacion: '' }
    else delete rechazos[codigo]
    setInspeccion({ ...inspeccion, [r.id_remito]: { ...datos, rechazos } })
  }

  function cambiarRechazo(r, codigo, campo, valor) {
    const datos = inspeccion[r.id_remito] || INSPECCION_INICIAL
    const rechazos = { ...datos.rechazos, [codigo]: { ...datos.rechazos[codigo], [campo]: valor } }
    setInspeccion({ ...inspeccion, [r.id_remito]: { ...datos, rechazos } })
  }

  return (
    <>
      <h2>Laboratorio - {usuario.nombre}</h2>
      {mensaje && <p className="mensaje">{mensaje}</p>}

      <h3>Remitos por recibir</h3>
      {remitos.length === 0 && <p>No hay remitos en tránsito.</p>}
      {remitos.map((r) => {
        const datos = inspeccion[r.id_remito] || INSPECCION_INICIAL
        const cambiar = (cambios) => setInspeccion({ ...inspeccion, [r.id_remito]: { ...datos, ...cambios } })
        const faltaDescribir = Object.values(datos.rechazos).some((x) => x.motivo === 'Otro' && !x.observacion?.trim())
        return (
          <div key={r.id_remito} className="tarjeta">
            <h4>Remito #{r.id_remito} desde {r.clinica}</h4>
            <p>Despachado {fechaHora(r.fecha_despacho)} | {r.transportista} | Precinto {r.precinto.codigo}</p>
            {r.novedades.length > 0 ? (
              <div className="novedades">
                <strong className="alerta">Novedades del traslado (revisá bien el precinto y las muestras):</strong>
                <ul>{r.novedades.map((n, i) => <li key={i}>{n}</li>)}</ul>
              </div>
            ) : <p className="ayuda">Traslado sin novedades.</p>}

            <strong>1. Precinto</strong>
            <div className="fila">
              <label className="check"><input type="radio" checked={datos.intacto} onChange={() => cambiar({ intacto: true })} />Intacto</label>
              <label className="check"><input type="radio" checked={!datos.intacto} onChange={() => cambiar({ intacto: false })} />Roto o violado</label>
              <input placeholder="Observaciones del precinto" value={datos.observaciones} onChange={(e) => cambiar({ observaciones: e.target.value })} />
            </div>

            <strong>2. Muestras</strong>
            {!datos.intacto ? (
              <p className="alerta">Con el precinto roto se rechazan todas las muestras del contenedor.</p>
            ) : (
              <>
                <p className="ayuda">Si alguna muestra llegó en mal estado, marcala y elegí el motivo. Las demás se reciben normalmente.</p>
                {r.muestras.map((m) => {
                  const marcada = datos.rechazos[m.codigo]
                  return (
                    <div key={m.codigo} className="fila">
                      <label className="check">
                        <input type="checkbox" checked={!!marcada} onChange={(e) => marcarRechazo(r, m.codigo, e.target.checked)} />
                        {m.codigo} - {m.tipo} {marcada ? <span className="alerta">(se rechaza)</span> : '(se recibe)'}
                      </label>
                      {marcada && (
                        <>
                          <select value={marcada.motivo} onChange={(e) => cambiarRechazo(r, m.codigo, 'motivo', e.target.value)}>
                            {motivos.map((x) => <option key={x}>{x}</option>)}
                          </select>
                          <input placeholder={marcada.motivo === 'Otro' ? 'Describí el motivo (obligatorio)' : 'Observación (opcional)'}
                            value={marcada.observacion} onChange={(e) => cambiarRechazo(r, m.codigo, 'observacion', e.target.value)} />
                        </>
                      )}
                    </div>
                  )
                })}
              </>
            )}
            <button disabled={faltaDescribir} onClick={() => recibir(r)}>Registrar recepción</button>
          </div>
        )
      })}

      <h3>Muestras para analizar</h3>
      {muestras.length === 0 && <p>No hay muestras recibidas pendientes.</p>}
      {muestras.map((m) => {
        const informe = resultado[m.codigo] || ''
        const rech = rechazo[m.codigo]
        return (
          <div key={m.codigo} className="tarjeta">
            <h4>{m.codigo} - {m.tipo}</h4>
            <p>Estudio: {m.tipo_estudio} | Paciente: {m.mascota} | {m.clinica}</p>
            <label>Resultado del análisis
              <textarea rows={4} maxLength={3000} value={informe}
                onChange={(e) => setResultado({ ...resultado, [m.codigo]: e.target.value })} />
            </label>
            <div className="fila">
              <button disabled={!informe.trim()}
                onClick={() => ejecutar(() => api.post(`/muestras/${m.codigo}/resultado`, {
                  matricula_bioquimico: usuario.matricula, informe,
                }), 'Resultado cargado.')}>Cargar resultado</button>
              {!rech && (
                <button className="secundario" onClick={() => setRechazo({ ...rechazo, [m.codigo]: { motivo: motivos[0], observacion: '' } })}>
                  La muestra no sirve
                </button>
              )}
            </div>
            {rech && (
              <div className="fila rechazo">
                <span>Rechazar por:</span>
                <select value={rech.motivo} onChange={(e) => setRechazo({ ...rechazo, [m.codigo]: { ...rech, motivo: e.target.value } })}>
                  {motivos.map((x) => <option key={x}>{x}</option>)}
                </select>
                <input placeholder={rech.motivo === 'Otro' ? 'Describí el motivo (obligatorio)' : 'Observación (opcional)'} value={rech.observacion}
                  onChange={(e) => setRechazo({ ...rechazo, [m.codigo]: { ...rech, observacion: e.target.value } })} />
                <button disabled={rech.motivo === 'Otro' && !rech.observacion.trim()}
                  onClick={() => ejecutar(() => api.post(`/muestras/${m.codigo}/rechazar`, {
                    matricula_bioquimico: usuario.matricula, motivo: rech.motivo, observacion: rech.observacion,
                  }), `Muestra ${m.codigo} rechazada. Se avisó al cliente para coordinar una nueva extracción.`)}>Confirmar rechazo</button>
                <button className="secundario" onClick={() => { const r = { ...rechazo }; delete r[m.codigo]; setRechazo(r) }}>Cancelar</button>
              </div>
            )}
          </div>
        )
      })}
    </>
  )
}
