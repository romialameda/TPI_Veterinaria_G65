import { useEffect, useRef, useState } from 'react'
import { api, fecha, fechaHora, hoy, hora, pesos } from '../api.js'
import CampoFecha from '../componentes/CampoFecha.jsx'

// Pantalla del veterinario:
//  1. Agenda del día: "Atender" crea la consulta con la mascota y el tipo del turno.
//  2. Urgencias de hoy: las registra recepción; el veterinario las abre y las atiende.
//  3. Ficha de la atención elegida: diagnóstico, órdenes de derivación y extracciones.
//  4. Historial de sus atenciones (solo consulta).
// Un turno se puede atender en cualquier momento del día del turno (por si el paciente llega antes
// o el anterior no vino), pero no un turno de otro día.
export default function Veterinario({ usuario }) {
  const [dia, setDia] = useState(hoy())
  const [turnos, setTurnos] = useState([])
  const [consultas, setConsultas] = useState([])
  const [idAbierta, setIdAbierta] = useState(null)   // Atención que se muestra en la ficha
  const [error, setError] = useState('')
  const refFicha = useRef(null)

  // Al abrir una atención, la pantalla baja hasta la ficha
  useEffect(() => {
    if (idAbierta) setTimeout(() => refFicha.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50)
  }, [idAbierta])

  async function cargarConsultas() {
    setConsultas(await api.get(`/veterinarios/${usuario.matricula}/consultas`))
  }

  async function cargarTurnos() {
    if (dia) setTurnos(await api.get(`/veterinarios/${usuario.matricula}/turnos?fecha=${dia}`))
  }

  useEffect(() => {
    cargarConsultas()
  }, [])

  useEffect(() => { cargarTurnos() }, [dia])

  async function atender(turno) {
    try {
      const consulta = await api.post(`/turnos/${turno.id_turno}/atender`)
      setError('')
      await cargarConsultas()
      await cargarTurnos()
      setIdAbierta(consulta.id_consulta)
    } catch (err) {
      setError(err.message)
    }
  }


  const abierta = consultas.find((c) => c.id_consulta === idAbierta)
  const urgenciasHoy = consultas.filter((c) => c.tipo_atencion === 'Urgencia' && c.fecha_hora.slice(0, 10) === hoy())

  return (
    <>
      <h2>Mis pacientes - {usuario.nombre}</h2>
      {error && <p className="mensaje">Error: {error}</p>}

      <div className="columnas">
        <div className="tarjeta ancha">
          <h3>1. Mi agenda</h3>
          <CampoFecha valor={dia} onCambio={setDia} />
          {turnos.length === 0 && <p>Sin turnos para este día.</p>}
          <table>
            <tbody>
              {turnos.map((t) => (
                <tr key={t.id_turno}>
                  <td>{hora(t.inicio)} a {hora(t.fin)}</td>
                  <td>{t.tipo}</td>
                  <td>{t.mascota} ({t.especie})<br /><span className="ayuda">{t.motivo}</span></td>
                  <td>
                    {t.atendido ? (
                      <button className="secundario" onClick={() => setIdAbierta(t.id_consulta)}>Atendido - ver</button>
                    ) : t.inicio.slice(0, 10) > hoy() ? (
                      <span className="ayuda">Se habilita el día del turno</span>
                    ) : t.inicio.slice(0, 10) < hoy() ? (
                      <span className="estado gris">No asistió</span>
                    ) : (
                      <button onClick={() => atender(t)}>Atender</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="tarjeta urgencia">
          <h3>2. Urgencias de hoy</h3>
          <p className="ayuda">Las registra recepción cuando llega un paciente sin turno.</p>
          {urgenciasHoy.length === 0 && <p>No hay urgencias.</p>}
          <ul>
            {urgenciasHoy.map((c) => (
              <li key={c.id_consulta}>
                {hora(c.fecha_hora)} - {c.mascota} ({c.responsable}): {c.motivo}{' '}
                <button className={c.diagnostico ? 'secundario' : ''} onClick={() => setIdAbierta(c.id_consulta)}>
                  {c.diagnostico ? 'Ver' : 'Atender'}
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div ref={refFicha} className="ancla">
        {abierta && <FichaAtencion key={abierta.id_consulta} consulta={abierta} onCambio={cargarConsultas} onCerrar={() => setIdAbierta(null)} />}
      </div>

      <h3>4. Historial de mis atenciones</h3>
      <table>
        <thead><tr><th>Fecha</th><th>Tipo</th><th>Mascota</th><th>Responsable</th><th>Diagnóstico</th><th className="numero">Costo</th></tr></thead>
        <tbody>
          {consultas.map((c) => (
            <tr key={c.id_consulta}>
              <td>{fechaHora(c.fecha_hora)}</td><td>{c.tipo_atencion}</td><td>{c.mascota}</td><td>{c.responsable}</td>
              <td>{c.diagnostico || <span className="ayuda">Pendiente</span>}</td><td className="numero">{pesos(c.costo)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  )
}

// Ficha de una atención: todo lo que el veterinario completa durante/después de atender
function FichaAtencion({ consulta: c, onCambio, onCerrar }) {
  const [diag, setDiag] = useState({ diagnostico: c.diagnostico, tratamiento: c.tratamiento })
  const [estudios, setEstudios] = useState([])
  const [tiposMuestra, setTiposMuestra] = useState([])
  const [laboratorios, setLaboratorios] = useState([])
  const [orden, setOrden] = useState({ tipo_estudio: '', id_laboratorio: '' })
  const [muestra, setMuestra] = useState({})   // { id_orden: tipo_muestra elegido }
  const [aviso, setAviso] = useState({})       // { seccion: texto } confirmaciones al lado de cada botón

  useEffect(() => {
    api.get('/estudios').then(setEstudios)
    api.get('/tipos-muestra').then(setTiposMuestra)
    api.get('/laboratorios').then((labs) => {
      setLaboratorios(labs)
      setOrden((o) => ({ ...o, id_laboratorio: o.id_laboratorio || String(labs[0]?.id_laboratorio || '') }))
    })
  }, [])

  // Ejecuta una acción y muestra el resultado al lado del botón correspondiente
  async function ejecutar(seccion, accion, texto) {
    try {
      const respuesta = await accion()
      setAviso({ ...aviso, [seccion]: '✓ ' + (typeof texto === 'function' ? texto(respuesta) : texto) })
      await onCambio()
      return true
    } catch (err) {
      setAviso({ ...aviso, [seccion]: '✗ ' + err.message })
      return false
    }
  }

  async function emitirOrden() {
    const ok = await ejecutar('orden', () => api.post(`/consultas/${c.id_consulta}/ordenes`, {
      tipo_estudio: orden.tipo_estudio, id_laboratorio: Number(orden.id_laboratorio),
    }), 'Orden emitida.')
    if (ok) setOrden({ ...orden, tipo_estudio: '' })
  }

  async function registrarExtraccion(idOrden) {
    const ok = await ejecutar('orden' + idOrden, () => api.post(`/ordenes/${idOrden}/muestras`, { tipo_muestra: muestra[idOrden] }),
      (r) => `Muestra registrada: etiquetá el tubo con el código ${r.codigo}.`)
    if (ok) setMuestra({ ...muestra, [idOrden]: '' })
  }

  return (
    <div className="tarjeta ficha">
      <div className="fila">
        <h3>3. {c.tipo_atencion} #{c.id_consulta} - {c.mascota}</h3>
        <button className="secundario derecha" onClick={onCerrar}>Cerrar</button>
      </div>
      <p>
        {fechaHora(c.fecha_hora)} | Responsable: {c.responsable} | Motivo: {c.motivo} | Costo: {pesos(c.costo)}
        {c.id_turno ? ' | Con turno' : ' | Sin turno'}
      </p>
      {c.vacunas_pendientes.length > 0 && <p className="alerta">Vacunas obligatorias pendientes: {c.vacunas_pendientes.join(', ')}</p>}

      <h4>Diagnóstico y tratamiento</h4>
      <div className="fila">
        <input placeholder="Diagnóstico" value={diag.diagnostico} onChange={(e) => setDiag({ ...diag, diagnostico: e.target.value })} />
        <input placeholder="Tratamiento" value={diag.tratamiento} onChange={(e) => setDiag({ ...diag, tratamiento: e.target.value })} />
        <button onClick={() => ejecutar('diag', () => api.put(`/consultas/${c.id_consulta}/diagnostico`, diag), 'Guardado.')}>Guardar diagnóstico</button>
        {aviso.diag && <span className="aviso">{aviso.diag}</span>}
      </div>

      <h4>Derivación al laboratorio</h4>
      <div className="fila">
        <select value={orden.tipo_estudio} onChange={(e) => setOrden({ ...orden, tipo_estudio: e.target.value })}>
          <option value="">Estudio a solicitar...</option>
          {estudios.map((e) => <option key={e}>{e}</option>)}
        </select>
        <select value={orden.id_laboratorio} onChange={(e) => setOrden({ ...orden, id_laboratorio: e.target.value })}>
          {laboratorios.map((l) => <option key={l.id_laboratorio} value={l.id_laboratorio}>{l.nombre}</option>)}
        </select>
        <button disabled={!orden.tipo_estudio} onClick={emitirOrden}>Emitir orden</button>
        {aviso.orden && <span className="aviso">{aviso.orden}</span>}
      </div>

      {c.ordenes.map((o) => (
        <div key={o.id_orden} className="orden">
          <strong>Orden #{o.id_orden}: {o.tipo_estudio}</strong> → {o.laboratorio}
          {o.muestras.length === 0 && <p className="ayuda">Todavía no se registraron muestras para esta orden.</p>}
          <ul>
            {o.muestras.map((m) => (
              <li key={m.codigo}>
                {m.codigo} - {m.tipo}{m.reextraccion_de && ` (nueva extracción de ${m.reextraccion_de})`}: <span className="estado">{m.estado}</span>
                {m.resultado && <> | Resultado: <span className="multilinea">{m.resultado.informe}</span></>}
                {m.estado === 'Rechazada' && m.motivo_rechazo && <span className="alerta"> {m.motivo_rechazo.split(': ').pop()}</span>}
                {m.reemplazada_por && <> (reemplazada por {m.reemplazada_por})</>}
                {m.estado === 'Rechazada' && !m.reemplazada_por && (
                  <button onClick={() => ejecutar('orden' + o.id_orden, () => api.post(`/muestras/${m.codigo}/reextraccion`),
                    (r) => `Nueva extracción registrada: código ${r.codigo}.`)}>Registrar nueva extracción</button>
                )}
              </li>
            ))}
          </ul>
          <div className="fila">
            <select value={muestra[o.id_orden] || ''} onChange={(e) => setMuestra({ ...muestra, [o.id_orden]: e.target.value })}>
              <option value="">Tipo de muestra extraída...</option>
              {tiposMuestra.map((t) => <option key={t}>{t}</option>)}
            </select>
            <button disabled={!muestra[o.id_orden]} onClick={() => registrarExtraccion(o.id_orden)}>
              {o.muestras.length === 0 ? 'Registrar extracción' : 'Agregar otra muestra'}
            </button>
            {aviso['orden' + o.id_orden] && <span className="aviso">{aviso['orden' + o.id_orden]}</span>}
          </div>
        </div>
      ))}

      <HistoriaClinica idMascota={c.id_mascota} idConsultaActual={c.id_consulta} actualizacion={JSON.stringify(c)} />
    </div>
  )
}

// Antecedentes de la mascota con TODOS los veterinarios: vacunas y consultas anteriores
function HistoriaClinica({ idMascota, idConsultaActual, actualizacion }) {
  const [m, setM] = useState(null)

  useEffect(() => { api.get(`/mascotas/${idMascota}/historia`).then(setM) }, [idMascota, actualizacion])

  if (!m) return null
  const anteriores = m.historia_clinica.filter((c) => c.id_consulta !== idConsultaActual)

  return (
    <details className="historia" open>
      <summary>Historia clínica de {m.nombre} ({m.especie}, {m.raza || 'sin raza'}, {m.peso} kg)</summary>

      <h4>Vacunas</h4>
      {m.vacunas.length === 0 && <p className="ayuda">Sin vacunas registradas.</p>}
      <ul>
        {m.vacunas.map((v, i) => (
          <li key={i}>{v.nombre} - aplicada {fecha(v.fecha)}, {v.vence < hoy() ? <span className="alerta">vencida el {fecha(v.vence)}</span> : `vigente hasta ${fecha(v.vence)}`}</li>
        ))}
      </ul>
      {m.vacunas_pendientes.length > 0 && <p className="alerta">Obligatorias pendientes: {m.vacunas_pendientes.join(', ')}</p>}

      <h4>Atenciones anteriores</h4>
      {anteriores.length === 0 && <p className="ayuda">Es su primera atención.</p>}
      {anteriores.map((c) => (
        <div key={c.id_consulta} className="orden">
          <strong>{fechaHora(c.fecha_hora)} - {c.tipo_atencion}</strong> con {c.veterinario} ({c.clinica})
          <div>Motivo: {c.motivo}</div>
          <div>Diagnóstico: {c.diagnostico || '-'} | Tratamiento: {c.tratamiento || '-'}</div>
          {c.ordenes.map((o) => (
            <div key={o.id_orden}>
              {o.tipo_estudio}:{' '}
              {o.muestras.map((mu) => (
                <span key={mu.codigo}>
                  {mu.tipo}{mu.reextraccion_de && ' (nueva extracción)'} <span className="estado">{mu.estado}</span>
                  {mu.reemplazada_por && ' (se volvió a extraer)'}
                  {mu.resultado && <> → <span className="multilinea">{mu.resultado.informe}</span></>}{' '}
                </span>
              ))}
            </div>
          ))}
        </div>
      ))}
    </details>
  )
}
