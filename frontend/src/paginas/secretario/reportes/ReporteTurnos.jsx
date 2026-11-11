import FiltrosReporte from '../../../componentes/FiltrosReporte.jsx'
import Tabla from '../../../componentes/Tabla.jsx'
import { GraficoBarras, GraficoBarrasHorizontal, GraficoTorta, Indicador } from '../../../componentes/Graficos.jsx'
import { fechaHora, hora } from '../../../api.js'
import { EncabezadoReporte, useReporte, useOpciones, opcionesDe } from './comun.jsx'

const ESTILO_ESTADO = { Atendido: 'estado', Ausente: 'estado alerta-tag', Cancelado: 'estado gris', Pendiente: 'estado pendiente' }

export default function ReporteTurnos() {
  const opciones = useOpciones()
  const { datos: r, filtros, setFiltros, error } = useReporte('turnos',
    { desde: '', hasta: '', clinica: '', veterinario: '', tipo: '', estado: '' })

  return (
    <>
      <EncabezadoReporte titulo="5. Turnos y asistencia" />
      {opciones && (
        <FiltrosReporte valores={filtros} onCambio={setFiltros} filtros={[
          { nombre: 'desde', etiqueta: 'Desde', tipo: 'fecha' },
          { nombre: 'hasta', etiqueta: 'Hasta', tipo: 'fecha' },
          { nombre: 'clinica', etiqueta: 'Sede', tipo: 'select', opciones: opcionesDe.clinicas(opciones) },
          { nombre: 'veterinario', etiqueta: 'Veterinario', tipo: 'select', opciones: opcionesDe.veterinarios(opciones) },
          { nombre: 'tipo', etiqueta: 'Tipo de turno', tipo: 'select', opciones: opcionesDe.lista(opciones.tipos_turno) },
          { nombre: 'estado', etiqueta: 'Estado', tipo: 'select', opciones: opcionesDe.lista(opciones.estados_turno) },
        ]} />
      )}
      {error && <p className="mensaje">Error: {error}</p>}
      {r && (
        <>
          <p className="ayuda">
            <strong>Ausente:</strong> turno de un día anterior que no se atendió. <strong>Pendiente:</strong> turno de hoy (o futuro) que todavía no se atendió.
            La asistencia se calcula sobre los turnos que ya pasaron (atendidos + ausentes).
          </p>
          <div className="indicadores">
            <Indicador titulo="Turnos dados" valor={r.total_turnos} />
            <Indicador titulo="Asistencia" valor={`${r.asistencia_pct}%`} detalle={`Ausentismo: ${r.ausentismo_pct}%`} />
            <Indicador titulo="Urgencias sin turno" valor={r.urgencias_sin_turno} detalle="Registradas por recepción" />
          </div>

          <h3>Por veterinario</h3>
          <Tabla filas={r.por_veterinario} columnas={[
            { campo: 'veterinario', titulo: 'Veterinario' },
            { campo: 'clinica', titulo: 'Sede' },
            { campo: 'turno_laboral', titulo: 'Turno' },
            { campo: 'total', titulo: 'Turnos', numero: true },
            { campo: 'Atendido', titulo: 'Atendidos', numero: true },
            { campo: 'Ausente', titulo: 'Ausentes', numero: true },
            { campo: 'Cancelado', titulo: 'Cancelados', numero: true },
            { campo: 'Pendiente', titulo: 'Pendientes', numero: true },
            { campo: 'asistencia_pct', titulo: 'Asistencia', numero: true, formato: (v, f) => (f.Atendido + f.Ausente ? `${v}%` : '-') },
          ]} />

          <h3>Detalle de turnos</h3>
          <Tabla filas={r.detalle} columnas={[
            { campo: 'inicio', titulo: 'Fecha', formato: (v, f) => `${fechaHora(v)} a ${hora(f.fin)}` },
            { campo: 'clinica', titulo: 'Sede' },
            { campo: 'veterinario', titulo: 'Veterinario' },
            { campo: 'paciente', titulo: 'Paciente' },
            { campo: 'responsable', titulo: 'Responsable' },
            { campo: 'tipo', titulo: 'Tipo' },
            { campo: 'motivo', titulo: 'Motivo' },
            { campo: 'estado', titulo: 'Estado', formato: (v) => <span className={ESTILO_ESTADO[v]}>{v}</span> },
          ]} />

          <h3>Gráficos</h3>
          <div className="graficos">
            <GraficoTorta titulo="Turnos por estado"
              datos={Object.entries(r.por_estado).filter(([, v]) => v).map(([etiqueta, valor]) => ({ etiqueta, valor }))} />
            <GraficoBarras titulo="Atendidos y ausentes por veterinario" series={['Atendidos', 'Ausentes']}
              datos={r.por_veterinario.map((f) => ({ etiqueta: f.veterinario, valores: [f.Atendido, f.Ausente] }))} />
            <GraficoBarrasHorizontal titulo="Turnos por día de la semana"
              datos={Object.entries(r.por_dia_semana).map(([etiqueta, valor]) => ({ etiqueta, valor }))} />
          </div>
        </>
      )}
    </>
  )
}
