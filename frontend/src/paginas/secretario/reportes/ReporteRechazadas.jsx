import FiltrosReporte from '../../../componentes/FiltrosReporte.jsx'
import Tabla from '../../../componentes/Tabla.jsx'
import { GraficoBarrasHorizontal, GraficoTorta, Indicador } from '../../../componentes/Graficos.jsx'
import { fechaHora } from '../../../api.js'
import { EncabezadoReporte, useReporte, useOpciones, opcionesDe } from './comun.jsx'

export default function ReporteRechazadas() {
  const opciones = useOpciones()
  const { datos: r, filtros, setFiltros, error } = useReporte('rechazadas',
    { desde: '', hasta: '', clinica: '', veterinario: '', especie: '', contenedor: '' })

  const aDatos = (objeto) => Object.entries(objeto).map(([etiqueta, valor]) => ({ etiqueta, valor }))

  return (
    <>
      <EncabezadoReporte titulo="2. Muestras rechazadas" />
      {opciones && (
        <FiltrosReporte valores={filtros} onCambio={setFiltros} filtros={[
          { nombre: 'desde', etiqueta: 'Extraídas desde', tipo: 'fecha' },
          { nombre: 'hasta', etiqueta: 'Hasta', tipo: 'fecha' },
          { nombre: 'clinica', etiqueta: 'Clínica', tipo: 'select', opciones: opcionesDe.clinicas(opciones) },
          { nombre: 'veterinario', etiqueta: 'Veterinario', tipo: 'select', opciones: opcionesDe.veterinarios(opciones) },
          { nombre: 'especie', etiqueta: 'Especie', tipo: 'select', opciones: opcionesDe.lista(opciones.especies) },
          { nombre: 'contenedor', etiqueta: 'Conservadora', tipo: 'select', opciones: opciones.conservadoras.map((n) => ({ valor: n, texto: `#${n}` })) },
        ]} />
      )}
      {error && <p className="mensaje">Error: {error}</p>}
      {r && (
        <>
          <div className="indicadores">
            <Indicador titulo="Muestras enviadas" valor={r.total_muestras} />
            <Indicador titulo="Rechazadas" valor={r.cantidad_rechazadas} detalle={`${r.tasa_rechazo_pct}% del total`} />
          </div>

          <h3>Detalle</h3>
          <Tabla filas={r.detalle} vacio="No hay muestras rechazadas para estos filtros." columnas={[
            { campo: 'codigo', titulo: 'Muestra' },
            { campo: 'tipo', titulo: 'Tipo' },
            { campo: 'fecha', titulo: 'Recepción', formato: fechaHora },
            { campo: 'paciente', titulo: 'Paciente' },
            { campo: 'especie', titulo: 'Especie' },
            { campo: 'veterinario', titulo: 'Veterinario' },
            { campo: 'contenedor', titulo: 'Conservadora', formato: (v) => `#${v}` },
            { campo: 'transportista', titulo: 'Transportista' },
            { campo: 'motivo', titulo: 'Motivo', formato: (v) => (v || '-').replace('Muestra rechazada', 'Rechazada') },
            { campo: 'novedades_traslado', titulo: 'Novedades del viaje', formato: (v) => v || 'Sin novedad' },
            { campo: 'reextraida', titulo: 'Re-extraída como', formato: (v) => v || 'No' },
          ]} />

          <h3>Gráficos</h3>
          <div className="graficos">
            <GraficoTorta titulo="Rechazadas sobre el total"
              datos={[{ etiqueta: 'Aceptadas', valor: r.total_muestras - r.cantidad_rechazadas }, { etiqueta: 'Rechazadas', valor: r.cantidad_rechazadas }]} />
            <GraficoBarrasHorizontal titulo="Rechazos por causa" datos={aDatos(r.por_causa)} />
            <GraficoBarrasHorizontal titulo="Rechazos por transportista" datos={aDatos(r.por_transportista)} color="#4F7AB8" />
            <GraficoBarrasHorizontal titulo="Rechazos por conservadora" datos={aDatos(r.por_contenedor)} color="#868228" />
          </div>
        </>
      )}
    </>
  )
}
