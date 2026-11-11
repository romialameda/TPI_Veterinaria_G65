import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, hoy, hora, pesos } from '../../api.js'
import CampoFecha from '../../componentes/CampoFecha.jsx'
import Urgencia from './Urgencia.jsx'

const TURNO_VACIO = { id_mascota: '', matricula_veterinario: '', tipo: 'Consulta', hora: '', motivo: '' }

export default function Turnos() {
  const navegar = useNavigate()
  const [dia, setDia] = useState(hoy())
  const [turnos, setTurnos] = useState([])
  const [mascotas, setMascotas] = useState([])
  const [veterinarios, setVeterinarios] = useState([])
  const [tipos, setTipos] = useState([])          // [{ tipo, duracion_minutos }]
  const [horarios, setHorarios] = useState([])    // Horarios libres del veterinario elegido
  const [nuevo, setNuevo] = useState(TURNO_VACIO)
  const [mensaje, setMensaje] = useState('')

  async function cargarTurnos() {
    if (dia) setTurnos(await api.get(`/turnos?fecha=${dia}`))
  }

  async function cargarHorarios() {
    if (!dia || !nuevo.matricula_veterinario) return setHorarios([])
    setHorarios(await api.get(`/turnos/horarios?fecha=${dia}&matricula_veterinario=${nuevo.matricula_veterinario}&tipo=${nuevo.tipo}`))
  }

  useEffect(() => {
    api.get('/mascotas').then(setMascotas)
    api.get('/veterinarios').then(setVeterinarios)
    api.get('/turnos/tipos').then(setTipos)
  }, [])

  useEffect(() => { cargarTurnos() }, [dia])
  useEffect(() => { cargarHorarios() }, [dia, nuevo.matricula_veterinario, nuevo.tipo])

  function elegirMascota(e) {
    // Opción especial: la mascota todavía no está cargada -> ir a registrarla
    if (e.target.value === 'registrar') navegar('/secretario/clientes')
    else setNuevo({ ...nuevo, id_mascota: e.target.value })
  }

  async function agendar(e) {
    e.preventDefault()
    try {
      await api.post('/turnos', {
        inicio: `${dia}T${nuevo.hora}`,
        tipo: nuevo.tipo,
        id_mascota: Number(nuevo.id_mascota),
        matricula_veterinario: nuevo.matricula_veterinario,
        motivo: nuevo.motivo,
      })
      setMensaje('Turno agendado.')
      setNuevo({ ...TURNO_VACIO, matricula_veterinario: nuevo.matricula_veterinario })
      cargarTurnos()
      cargarHorarios()
    } catch (err) {
      setMensaje('Error: ' + err.message)
    }
  }

  async function cancelar(id) {
    await api.post(`/turnos/${id}/cancelar`)
    cargarTurnos()
    cargarHorarios()
  }

  const campo = (nombre) => ({ value: nuevo[nombre], onChange: (e) => setNuevo({ ...nuevo, [nombre]: e.target.value }) })
  const diaPasado = dia && dia < hoy()

  return (
    <>
      <h2>Agenda de turnos</h2>
      <label>Día <CampoFecha valor={dia} onCambio={setDia} /></label>
      {dia === hoy() && <p className="ayuda">Es hoy: los horarios que ya pasaron no se ofrecen para nuevos turnos.</p>}
      {mensaje && <p className="mensaje">{mensaje}</p>}

      <div className="columnas">
        <div className="pila">
        <form onSubmit={agendar} className="tarjeta">
          <h3>Nuevo turno</h3>
          {diaPasado && <p className="alerta">No se pueden dar turnos para un día que ya pasó.</p>}
          <label>Mascota
            <select value={nuevo.id_mascota} onChange={elegirMascota} required>
              <option value="">Elegir...</option>
              {mascotas.map((m) => <option key={m.id_mascota} value={m.id_mascota}>{m.nombre} ({m.especie}) - {m.responsable}</option>)}
              <option value="registrar">➕ Mascota no registrada (ir a registrarla)</option>
            </select>
          </label>
          <label>Veterinario
            <select value={nuevo.matricula_veterinario} onChange={(e) => setNuevo({ ...nuevo, matricula_veterinario: e.target.value, hora: '' })} required>
              <option value="">Elegir...</option>
              {veterinarios.map((v) => <option key={v.matricula} value={v.matricula}>{v.nombre_completo} - {v.clinica} - {v.horario}</option>)}
            </select>
          </label>
          <label>Tipo de turno
            <select value={nuevo.tipo} onChange={(e) => setNuevo({ ...nuevo, tipo: e.target.value, hora: '' })}>
              {tipos.map((t) => <option key={t.tipo} value={t.tipo}>{t.tipo} ({t.duracion_minutos} min) - {pesos(t.precio)}</option>)}
            </select>
          </label>
          {tipos.find((t) => t.tipo === nuevo.tipo) && (
            <p className="precio">Precio a informar al cliente: <strong>{pesos(tipos.find((t) => t.tipo === nuevo.tipo).precio)}</strong></p>
          )}
          <label>Horario
            <select {...campo('hora')} required disabled={!nuevo.matricula_veterinario || diaPasado}>
              <option value="">{nuevo.matricula_veterinario ? (horarios.length ? 'Elegir...' : 'Sin horarios libres') : 'Primero elegí el veterinario'}</option>
              {horarios.map((h) => <option key={h} value={h}>{h}</option>)}
            </select>
          </label>
          <label>Motivo <input {...campo('motivo')} required /></label>
          <button type="submit" disabled={diaPasado}>Agendar</button>
        </form>
        <Urgencia mascotas={mascotas} veterinarios={veterinarios} />
        </div>

        <div className="tarjeta ancha">
          <h3>Turnos del día</h3>
          {turnos.length === 0 && <p>No hay turnos.</p>}
          <div className="tabla-scroll">
          <table className="compacta">
            <thead><tr><th>Horario</th><th>Paciente</th><th>Veterinario</th><th>Motivo</th><th className="numero">Precio</th><th>Estado</th></tr></thead>
            <tbody>
              {turnos.map((t) => (
                <tr key={t.id_turno} className={t.cancelado ? 'cancelado' : ''}>
                  <td className="nowrap">{hora(t.inicio)} a {hora(t.fin)}<small>{t.tipo}</small></td>
                  <td>{t.mascota} ({t.especie})<small>{t.responsable}</small></td>
                  <td>{t.veterinario}<small>{t.clinica}</small></td>
                  <td>{t.motivo}</td>
                  <td className="numero">{pesos(t.precio)}</td>
                  <td>
                    {t.cancelado ? 'Cancelado'
                      : t.atendido ? <span className="estado">Atendido</span>
                      : dia < hoy() ? <span className="estado gris">No asistió</span>
                      : <button onClick={() => cancelar(t.id_turno)}>Cancelar</button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        </div>
      </div>
    </>
  )
}
