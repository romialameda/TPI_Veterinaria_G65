import FiltrosReporte from '../../../componentes/FiltrosReporte.jsx'
import Tabla from '../../../componentes/Tabla.jsx'
import { GraficoBarras, GraficoBarrasHorizontal, GraficoTorta, Indicador } from '../../../componentes/Graficos.jsx'
import { fechaHora } from '../../../api.js'
import { EncabezadoReporte, useReporte, useOpciones, opcionesDe } from './comun.jsx'

export default function ReporteAtenciones() {
  const opciones = useOpciones()
  const { datos: r, filtros, setFiltros, error } = useReporte('atenciones', {
    desde: '', hasta: '', clinica: '', veterinario: '', responsable: '', paciente: '', especie: '', tipo_atencion: '',
  })

  // Al cambiar el responsable se borra el paciente elegido (puede no ser suyo)
  function cambiarFiltros(nuevos) {
    setFiltros(nuevos.responsable !== filtros.responsable ? { ...nuevos, paciente: '' } : nuevos)
  }

  // Pacientes: si hay responsable elegido, solo sus mascotas (evita confundir mascotas con el mismo nombre)
  const pacientes = opciones
    ? opciones.mascotas
      .filter((m) => !filtros.responsable || m.dni_responsable === filtros.responsable)
      .map((m) => {
        const dueño = opciones.clientes.find((c) => c.dni === m.dni_responsable)
        return { valor: m.id, texto: filtros.responsable ? m.nombre : `${m.nombre} (${dueño?.nombre})` }
      })
    : []

  return (
    <>
      <EncabezadoReporte titulo="1. Atenciones clínicas y derivaciones" />
      {opciones && (
        <FiltrosReporte valores={filtros} onCambio={cambiarFiltros} filtros={[
          { nombre: 'desde', etiqueta: 'Desde', tipo: 'fecha' },
          { nombre: 'hasta', etiqueta: 'Hasta', tipo: 'fecha' },
          { nombre: 'clinica', etiqueta: 'Clínica', tipo: 'select', opciones: opcionesDe.clinicas(opciones) },
          { nombre: 'veterinario', etiqueta: 'Veterinario', tipo: 'select', opciones: opcionesDe.veterinarios(opciones) },
          { nombre: 'responsable', etiqueta: 'Responsable', tipo: 'select', opciones: opciones.clientes.map((c) => ({ valor: c.dni, texto: `${c.nombre} (${c.dni})` })) },
          { nombre: 'paciente', etiqueta: 'Paciente', tipo: 'select', opciones: pacientes },
          { nombre: 'especie', etiqueta: 'Especie', tipo: 'select', opciones: opcionesDe.lista(opciones.especies) },
          { nombre: 'tipo_atencion', etiqueta: 'Tipo de atención', tipo: 'select', opciones: opcionesDe.lista(opciones.tipos_atencion) },
        ]} />
      )}
      {error && <p className="mensaje">Error: {error}</p>}
      {r && (
        <>
          <div className="indicadores">
            <Indicador titulo="Atenciones" valor={r.total_consultas} />
            <Indicador titulo="Con derivación al laboratorio" valor={r.consultas_derivadas} detalle={`${r.tasa_derivacion_pct}% del total`} />
          </div>

          <h3>Detalle de atenciones</h3>
          <Tabla filas={r.detalle} columnas={[
            { campo: 'fecha', titulo: 'Fecha', formato: fechaHora },
            { campo: 'clinica', titulo: 'Clínica' },
            { campo: 'veterinario', titulo: 'Veterinario' },
            { campo: 'paciente', titulo: 'Paciente' },
            { campo: 'responsable', titulo: 'Responsable' },
            { campo: 'especie', titulo: 'Especie' },
            { campo: 'tipo', titulo: 'Tipo' },
            { campo: 'motivo', titulo: 'Motivo' },
            { campo: 'estudios', titulo: 'Estudios derivados', formato: (v) => v || '-' },
          ]} />

          <h3>Resumen por veterinario</h3>
          <Tabla filas={r.por_veterinario} columnas={[
            { campo: 'veterinario', titulo: 'Veterinario' },
            { campo: 'clinica', titulo: 'Clínica' },
            { campo: 'total', titulo: 'Atenciones', numero: true },
            { campo: 'derivadas', titulo: 'Derivadas', numero: true },
            { campo: 'tasa_derivacion_pct', titulo: '% derivación', numero: true, formato: (v) => `${v}%` },
          ]} />

          <h3>Gráficos</h3>
          <div className="graficos">
            <GraficoBarras titulo="Atenciones y derivaciones por clínica" series={['Atenciones', 'Derivadas']}
              datos={Object.entries(r.por_clinica).map(([clinica, f]) => ({ etiqueta: clinica, valores: [f.total, f.derivadas] }))} />
            <GraficoTorta titulo="Atenciones por tipo" datos={Object.entries(r.por_tipo).map(([etiqueta, valor]) => ({ etiqueta, valor }))} />
            <GraficoBarrasHorizontal titulo="Estudios derivados" datos={r.por_estudio.map(([etiqueta, valor]) => ({ etiqueta, valor }))} />
          </div>
        </>
      )}
    </>
  )
}
