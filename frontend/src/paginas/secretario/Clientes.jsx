import { useEffect, useState } from 'react'
import { api, fecha, hoy } from '../../api.js'
import CampoFecha from '../../componentes/CampoFecha.jsx'

const CLIENTE_VACIO = { dni: '', nombre: '', apellido: '', telefono: '', email: '', contrasena: '' }
const MASCOTA_VACIA = { nombre: '', especie: 'Canino', raza: '', fecha_nacimiento: '', peso: '', dni_responsable: '' }
const VACUNA_VACIA = { id_mascota: '', nombre: '', fecha_aplicacion: hoy() }

export default function Clientes() {
  const [clientes, setClientes] = useState([])
  const [mascotas, setMascotas] = useState([])
  const [nuevoCliente, setNuevoCliente] = useState(CLIENTE_VACIO)
  const [nuevaMascota, setNuevaMascota] = useState(MASCOTA_VACIA)
  const [nuevaVacuna, setNuevaVacuna] = useState(VACUNA_VACIA)
  const [mensaje, setMensaje] = useState('')
  const [vacunasDisponibles, setVacunasDisponibles] = useState([])

  async function cargar() {
    setClientes(await api.get('/clientes'))
    setMascotas(await api.get('/mascotas'))
  }

  useEffect(() => { cargar() }, [])

  // Al elegir la mascota, se cargan las vacunas del catálogo para su especie
  useEffect(() => {
    const mascota = mascotas.find((m) => String(m.id_mascota) === nuevaVacuna.id_mascota)
    if (mascota) api.get('/vacunas?especie=' + mascota.especie).then(setVacunasDisponibles)
    else setVacunasDisponibles([])
  }, [nuevaVacuna.id_mascota, mascotas])

  async function guardar(e, accion) {
    e.preventDefault()
    try {
      setMensaje(await accion())
      await cargar()
    } catch (err) {
      setMensaje('Error: ' + err.message)
    }
  }

  const altaCliente = (e) => guardar(e, async () => {
    await api.post('/clientes', nuevoCliente)
    setNuevoCliente(CLIENTE_VACIO)
    return `Cliente creado. Usuario para ingresar: ${nuevoCliente.dni}`
  })

  const altaMascota = (e) => guardar(e, async () => {
    const m = await api.post('/mascotas', {
      ...nuevaMascota,
      peso: Number(nuevaMascota.peso.replace(',', '.')),
      fecha_nacimiento: nuevaMascota.fecha_nacimiento || null,
    })
    setNuevaMascota(MASCOTA_VACIA)
    return `Mascota ${m.nombre} registrada.`
  })

  const altaVacuna = (e) => guardar(e, async () => {
    await api.post(`/mascotas/${nuevaVacuna.id_mascota}/vacunas`, nuevaVacuna)
    setNuevaVacuna(VACUNA_VACIA)
    return 'Vacuna registrada.'
  })

  // Actualiza un campo de un formulario: campo(setNuevoCliente, nuevoCliente, 'dni')
  const campo = (set, objeto, nombre) => ({
    value: objeto[nombre],
    onChange: (e) => set({ ...objeto, [nombre]: e.target.value }),
  })

  return (
    <>
      <h2>Clientes y mascotas</h2>
      {mensaje && <p className="mensaje">{mensaje}</p>}

      <div className="columnas">
        <form onSubmit={altaCliente} className="tarjeta">
          <h3>Nuevo cliente</h3>
          <label>DNI <input {...campo(setNuevoCliente, nuevoCliente, 'dni')} required /></label>
          <label>Nombre <input {...campo(setNuevoCliente, nuevoCliente, 'nombre')} required /></label>
          <label>Apellido <input {...campo(setNuevoCliente, nuevoCliente, 'apellido')} required /></label>
          <label>Teléfono <input {...campo(setNuevoCliente, nuevoCliente, 'telefono')} required /></label>
          <label>Email <input type="email" {...campo(setNuevoCliente, nuevoCliente, 'email')} /></label>
          <label>Contraseña para ingresar <input {...campo(setNuevoCliente, nuevoCliente, 'contrasena')} required /></label>
          <button type="submit">Crear cliente</button>
        </form>

        <form onSubmit={altaMascota} className="tarjeta">
          <h3>Nueva mascota</h3>
          <label>Responsable
            <select {...campo(setNuevaMascota, nuevaMascota, 'dni_responsable')} required>
              <option value="">Elegir...</option>
              {clientes.map((c) => <option key={c.dni} value={c.dni}>{c.nombre_completo} ({c.dni})</option>)}
            </select>
          </label>
          <label>Nombre <input {...campo(setNuevaMascota, nuevaMascota, 'nombre')} required /></label>
          <label>Especie
            <select {...campo(setNuevaMascota, nuevaMascota, 'especie')}>
              <option>Canino</option>
              <option>Felino</option>
            </select>
          </label>
          <label>Raza <input {...campo(setNuevaMascota, nuevaMascota, 'raza')} /></label>
          <label>Fecha de nacimiento
            <CampoFecha valor={nuevaMascota.fecha_nacimiento} max={hoy()} onCambio={(v) => setNuevaMascota({ ...nuevaMascota, fecha_nacimiento: v })} />
          </label>
          <label>Peso (kg) <input inputMode="decimal" pattern="\d+([.,]\d+)?" title="Número, por ejemplo 4,5" {...campo(setNuevaMascota, nuevaMascota, 'peso')} required /></label>
          <button type="submit">Registrar mascota</button>
        </form>

        <form onSubmit={altaVacuna} className="tarjeta">
          <h3>Registrar vacuna</h3>
          <label>Mascota
            <select value={nuevaVacuna.id_mascota} onChange={(e) => setNuevaVacuna({ ...nuevaVacuna, id_mascota: e.target.value, nombre: '' })} required>
              <option value="">Elegir...</option>
              {mascotas.map((m) => <option key={m.id_mascota} value={m.id_mascota}>{m.nombre} ({m.responsable})</option>)}
            </select>
          </label>
          <label>Vacuna
            <select {...campo(setNuevaVacuna, nuevaVacuna, 'nombre')} required disabled={!nuevaVacuna.id_mascota}>
              <option value="">{nuevaVacuna.id_mascota ? 'Elegir...' : 'Primero elegí la mascota'}</option>
              {vacunasDisponibles.map((v) => <option key={v.nombre} value={v.nombre}>{v.nombre}{v.obligatoria ? ' (obligatoria)' : ''}</option>)}
            </select>
          </label>
          <label>Fecha
            <CampoFecha valor={nuevaVacuna.fecha_aplicacion} max={hoy()} onCambio={(v) => setNuevaVacuna({ ...nuevaVacuna, fecha_aplicacion: v })} required />
          </label>
          <button type="submit">Registrar vacuna</button>
        </form>
      </div>

      <h3>Clientes</h3>
      <table>
        <thead><tr><th>DNI</th><th>Nombre</th><th>Teléfono</th><th>Email</th><th>Mascotas</th></tr></thead>
        <tbody>
          {clientes.map((c) => (
            <tr key={c.dni}><td>{c.dni}</td><td>{c.nombre_completo}</td><td>{c.telefono}</td><td>{c.email}</td><td>{c.cantidad_mascotas}</td></tr>
          ))}
        </tbody>
      </table>

      <h3>Mascotas</h3>
      <table>
        <thead><tr><th>Nombre</th><th>Especie</th><th>Raza</th><th>Nacimiento</th><th>Peso</th><th>Responsable</th></tr></thead>
        <tbody>
          {mascotas.map((m) => (
            <tr key={m.id_mascota}><td>{m.nombre}</td><td>{m.especie}</td><td>{m.raza}</td><td>{fecha(m.fecha_nacimiento)}</td><td>{m.peso} kg</td><td>{m.responsable}</td></tr>
          ))}
        </tbody>
      </table>
    </>
  )
}
