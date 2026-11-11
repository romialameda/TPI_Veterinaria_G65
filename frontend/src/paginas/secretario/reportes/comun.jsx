import { useEffect, useState } from 'react'
import { NavLink, Link } from 'react-router-dom'
import { api } from '../../../api.js'
import { consulta } from '../../../componentes/FiltrosReporte.jsx'

export const REPORTES = [
  { ruta: 'atenciones', titulo: 'Atenciones y derivaciones', descripcion: 'Atenciones por clínica, veterinario y tipo; estudios derivados al laboratorio.' },
  { ruta: 'rechazadas', titulo: 'Muestras rechazadas', descripcion: 'Muestras rechazadas (precinto roto o rechazo puntual), por causa, conservadora y transportista.' },
  { ruta: 'facturacion', titulo: 'Facturación', descripcion: 'Lo facturado por clínica, desglosado en atenciones y servicios de laboratorio.' },
  { ruta: 'tiempos', titulo: 'Tiempos y demoras', descripcion: 'Tránsito al laboratorio, procesamiento y demora total hasta el resultado por estudio.' },
  { ruta: 'turnos', titulo: 'Turnos y asistencia', descripcion: 'Turnos atendidos, ausentes, cancelados y pendientes por veterinario, sede y día; urgencias sin turno.' },
]

// Encabezado común: volver al menú + pestañas para pasar de un reporte a otro
export function EncabezadoReporte({ titulo }) {
  return (
    <>
      <Link to="/secretario/reportes" className="volver">← Todos los reportes</Link>
      <nav className="pestanas">
        {REPORTES.map((r) => <NavLink key={r.ruta} to={`/secretario/reportes/${r.ruta}`}>{r.titulo}</NavLink>)}
      </nav>
      <h2>{titulo}</h2>
    </>
  )
}

// Pide el reporte a la API cada vez que cambian los filtros
export function useReporte(ruta, filtrosIniciales) {
  const [filtros, setFiltros] = useState(filtrosIniciales)
  const [datos, setDatos] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get(`/reportes/${ruta}${consulta(filtros)}`)
      .then((d) => { setDatos(d); setError('') })
      .catch((e) => setError(e.message))
  }, [ruta, JSON.stringify(filtros)])

  return { datos, filtros, setFiltros, error }
}

// Opciones para los desplegables de filtros (clínicas, veterinarios, especies...)
export function useOpciones() {
  const [opciones, setOpciones] = useState(null)
  useEffect(() => { api.get('/reportes/opciones').then(setOpciones) }, [])
  return opciones
}

export const opcionesDe = {
  clinicas: (o) => o.clinicas.map((c) => ({ valor: c.id, texto: c.nombre })),
  veterinarios: (o) => o.veterinarios.map((v) => ({ valor: v.matricula, texto: `${v.nombre} (${v.clinica})` })),
  lista: (lista) => lista.map((x) => ({ valor: x, texto: x })),
}
