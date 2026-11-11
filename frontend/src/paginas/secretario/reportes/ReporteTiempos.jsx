import FiltrosReporte from '../../../componentes/FiltrosReporte.jsx'
import Tabla from '../../../componentes/Tabla.jsx'
import { GraficoBarrasHorizontal, Indicador } from '../../../componentes/Graficos.jsx'
import { EncabezadoReporte, useReporte, useOpciones, opcionesDe } from './comun.jsx'

const horas = (v) => (v == null ? 'sin datos' : `${v} hs`)

export default function ReporteTiempos() {
  const opciones = useOpciones()
  const { datos: r, filtros, setFiltros, error } = useReporte('tiempos',
    { desde: '', hasta: '', clinica: '', tipo_estudio: '', tipo_muestra: '' })

  const aDatos = (objeto) => Object.entries(objeto).filter(([, v]) => v != null).map(([etiqueta, valor]) => ({ etiqueta, valor }))

  // Para muestras que todavía no llegaron a cada etapa
  const sinDato = (v, fila, texto) => {
    if (v != null) return `${v} hs`
    if (fila.estado === 'Rechazada') return 'Rechazada'
    if (fila.estado === 'Extraída' || fila.estado === 'Empaquetada') return 'Todavía no se envió'
    return texto
  }

  return (
    <>
      <EncabezadoReporte titulo="4. Tiempos y demoras de las muestras" />
      {opciones && (
        <FiltrosReporte valores={filtros} onCambio={setFiltros} filtros={[
          { nombre: 'desde', etiqueta: 'Extraídas desde', tipo: 'fecha' },
          { nombre: 'hasta', etiqueta: 'Hasta', tipo: 'fecha' },
          { nombre: 'clinica', etiqueta: 'Clínica de origen', tipo: 'select', opciones: opcionesDe.clinicas(opciones) },
          { nombre: 'tipo_estudio', etiqueta: 'Estudio', tipo: 'select', opciones: opcionesDe.lista(opciones.estudios) },
          { nombre: 'tipo_muestra', etiqueta: 'Tipo de muestra', tipo: 'select', opciones: opcionesDe.lista(opciones.tipos_muestra) },
        ]} />
      )}
      {error && <p className="mensaje">Error: {error}</p>}
      {r && (
        <>
          <p className="ayuda">
            <strong>Tránsito:</strong> solo ida, desde que sale de la clínica hasta que llega al laboratorio (las muestras no vuelven).{' '}
            <strong>Procesamiento:</strong> desde que el laboratorio la recibe hasta que carga el resultado.{' '}
            <strong>Demora total:</strong> desde la extracción hasta el resultado; es el tiempo aproximado que hay que informarle al cliente.
          </p>
          <div className="indicadores">
            <Indicador titulo="Demora total promedio" valor={horas(r.promedio_total_hs)} detalle="De la extracción al resultado" />
            <Indicador titulo="Tránsito promedio (ida)" valor={horas(r.promedio_transito_hs)} detalle={`Máximo: ${horas(r.maximo_transito_hs)}`} />
            <Indicador titulo="Procesamiento promedio" valor={horas(r.promedio_procesamiento_hs)} detalle="De la recepción al resultado" />
          </div>

          <h3>Demora estimada por estudio</h3>
          <Tabla vacio="Todavía no hay resultados cargados para estos filtros."
            filas={Object.entries(r.demora_total_por_estudio_hs).map(([estudio, total]) => ({
              estudio, total, procesamiento: r.procesamiento_por_estudio_hs[estudio],
            }))}
            columnas={[
              { campo: 'estudio', titulo: 'Estudio' },
              { campo: 'total', titulo: 'Demora total promedio', numero: true, formato: (v) => <strong>{horas(v)}</strong> },
              { campo: 'procesamiento', titulo: 'De eso, en el laboratorio', numero: true, formato: horas },
            ]} />

          <h3>Detalle por muestra</h3>
          <Tabla filas={r.detalle} columnas={[
            { campo: 'codigo', titulo: 'Muestra' },
            { campo: 'tipo', titulo: 'Tipo' },
            { campo: 'estudio', titulo: 'Estudio' },
            { campo: 'clinica', titulo: 'Clínica' },
            { campo: 'estado', titulo: 'Estado' },
            { campo: 'horas_transito', titulo: 'Tránsito', numero: true, formato: (v, f) => sinDato(v, f, 'Todavía no llegó') },
            { campo: 'horas_procesamiento', titulo: 'Procesamiento', numero: true, formato: (v, f) => sinDato(v, f, 'Sin resultado todavía') },
            { campo: 'horas_total', titulo: 'Demora total', numero: true, formato: (v, f) => sinDato(v, f, 'Sin resultado todavía') },
          ]} />

          <h3>Gráficos</h3>
          <div className="graficos">
            <GraficoBarrasHorizontal titulo="Demora total promedio por estudio" formato={horas} datos={aDatos(r.demora_total_por_estudio_hs)} />
            <GraficoBarrasHorizontal titulo="Tránsito promedio por ruta (ida)" formato={horas} datos={aDatos(r.promedio_por_ruta_hs)} color="#4F7AB8" />
          </div>
        </>
      )}
    </>
  )
}
