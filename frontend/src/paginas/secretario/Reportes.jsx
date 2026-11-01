import { useEffect, useState } from 'react'
import { api, fecha, pesos } from '../../api.js'

const horas = (valor) => (valor == null ? 'sin datos' : `${valor} hs`)

export default function Reportes() {
  const [r, setR] = useState(null)

  useEffect(() => { api.get('/reportes').then(setR) }, [])

  if (!r) return <p>Cargando...</p>

  return (
    <>
      <h2>Reportes</h2>

      <div className="tarjeta">
        <h3>1. Atenciones clínicas y derivaciones</h3>
        <p>Total: {r.atenciones.total_consultas} atenciones | Derivadas: {r.atenciones.consultas_derivadas} ({r.atenciones.tasa_derivacion_pct}%)</p>
        <table>
          <thead><tr><th>Clínica</th><th>Atenciones</th><th>Por tipo</th><th>% derivación</th><th>Estudios pedidos</th></tr></thead>
          <tbody>
            {Object.entries(r.atenciones.por_clinica).map(([clinica, f]) => (
              <tr key={clinica}>
                <td>{clinica}</td><td>{f.total}</td>
                <td>{Object.entries(f.por_tipo).map(([t, n]) => `${t}: ${n}`).join(', ')}</td>
                <td>{f.tasa_derivacion_pct}%</td>
                <td>{f.estudios.map(([e, n]) => `${e} (${n})`).join(', ')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="tarjeta">
        <h3>2. Muestras rechazadas por fallas en el transporte</h3>
        <p>{r.rechazadas.cantidad_rechazadas} de {r.rechazadas.total_muestras} muestras ({r.rechazadas.tasa_rechazo_pct}%)</p>
        <table>
          <thead><tr><th>Muestra</th><th>Paciente</th><th>Remito</th><th>Transportista</th><th>Observación del precinto</th><th>Re-extraída</th></tr></thead>
          <tbody>
            {r.rechazadas.detalle.map((d) => (
              <tr key={d.codigo}><td>{d.codigo} ({d.tipo})</td><td>{d.paciente}</td><td>#{d.remito}</td><td>{d.transportista}</td><td>{d.observacion_precinto}</td><td>{d.reextraida || 'No'}</td></tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="tarjeta">
        <h3>3. Tratamientos aplicados y vacunas pendientes</h3>
        <table>
          <thead><tr><th>Paciente</th><th>Responsable</th><th>Tratamientos</th><th>Vacunas pendientes</th></tr></thead>
          <tbody>
            {r.vacunas.pacientes.map((p) => (
              <tr key={p.paciente + p.responsable}>
                <td>{p.paciente} ({p.especie})</td><td>{p.responsable} - {p.contacto}</td>
                <td>{p.tratamientos.map((t) => `${fecha(t.fecha.slice(0, 10))}: ${t.tratamiento}`).join(' | ') || '-'}</td>
                <td className={p.vacunas_pendientes.length ? 'alerta' : ''}>{p.vacunas_pendientes.join(', ') || 'Al día'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="tarjeta">
        <h3>4. Facturación por clínica y servicios de laboratorio</h3>
        <table>
          <thead><tr><th>Clínica</th><th>Consultas</th><th>Muestras analizadas</th><th>Costo laboratorio</th><th>Neto</th></tr></thead>
          <tbody>
            {Object.entries(r.facturacion.por_clinica).map(([clinica, f]) => (
              <tr key={clinica}>
                <td>{clinica}</td><td className="numero">{pesos(f.ingresos_consultas)}</td><td>{f.muestras_analizadas}</td>
                <td className="numero">{pesos(f.costo_laboratorio)}</td><td className="numero">{pesos(f.balance_neto)}</td>
              </tr>
            ))}
            <tr>
              <th>Total</th><th className="numero">{pesos(r.facturacion.total_ingresos)}</th><th></th>
              <th className="numero">{pesos(r.facturacion.total_costo_laboratorio)}</th><th className="numero">{pesos(r.facturacion.total_balance_neto)}</th>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="tarjeta">
        <h3>5. Tiempos de tránsito y procesamiento</h3>
        <p>Tránsito promedio: {horas(r.tiempos.promedio_transito_hs)} (máximo {horas(r.tiempos.maximo_transito_hs)})</p>
        <p>Procesamiento promedio en laboratorio: {horas(r.tiempos.promedio_procesamiento_hs)}</p>
        <ul>
          {Object.entries(r.tiempos.promedio_por_ruta_hs).map(([ruta, h]) => <li key={ruta}>{ruta}: {horas(h)}</li>)}
        </ul>
      </div>
    </>
  )
}
