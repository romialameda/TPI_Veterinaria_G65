import FiltrosReporte from '../../../componentes/FiltrosReporte.jsx'
import Tabla from '../../../componentes/Tabla.jsx'
import { GraficoBarras, GraficoBarrasHorizontal, GraficoTorta, Indicador } from '../../../componentes/Graficos.jsx'
import { pesos } from '../../../api.js'
import { EncabezadoReporte, useReporte, useOpciones, opcionesDe } from './comun.jsx'

// Lo facturado a los clientes, por clínica, desglosado en atenciones y servicios de laboratorio
export default function ReporteFacturacion() {
  const opciones = useOpciones()
  const { datos: r, filtros, setFiltros, error } = useReporte('facturacion', { desde: '', hasta: '', clinica: '', veterinario: '' })

  const filas = r ? Object.entries(r.por_clinica).map(([clinica, f]) => ({ clinica, ...f })) : []

  return (
    <>
      <EncabezadoReporte titulo="3. Facturación por clínica y servicios de laboratorio" />
      {opciones && (
        <FiltrosReporte valores={filtros} onCambio={setFiltros} filtros={[
          { nombre: 'desde', etiqueta: 'Desde', tipo: 'fecha' },
          { nombre: 'hasta', etiqueta: 'Hasta', tipo: 'fecha' },
          { nombre: 'clinica', etiqueta: 'Clínica', tipo: 'select', opciones: opcionesDe.clinicas(opciones) },
          { nombre: 'veterinario', etiqueta: 'Veterinario', tipo: 'select', opciones: opcionesDe.veterinarios(opciones) },
        ]} />
      )}
      {error && <p className="mensaje">Error: {error}</p>}
      {r && (
        <>
          <p className="ayuda">
            Atenciones: precio fijo según el tipo (consulta, control o urgencia). Laboratorio: cada muestra analizada
            se le cobra al cliente {pesos(r.arancel_analisis_por_muestra)}.
          </p>
          <div className="indicadores">
            <Indicador titulo="Total facturado" valor={pesos(r.total_facturado)} />
            <Indicador titulo="Por atenciones" valor={pesos(r.total_atenciones)} />
            <Indicador titulo="Por servicios de laboratorio" valor={pesos(r.total_laboratorio)} />
          </div>

          <h3>Por clínica</h3>
          <Tabla filas={filas} columnas={[
            { campo: 'clinica', titulo: 'Clínica' },
            { campo: 'cantidad_atenciones', titulo: 'Atenciones', numero: true },
            { campo: 'atenciones', titulo: 'Facturado por atenciones', numero: true, formato: pesos },
            { campo: 'muestras_analizadas', titulo: 'Muestras analizadas', numero: true },
            { campo: 'laboratorio', titulo: 'Facturado por laboratorio', numero: true, formato: pesos },
            { campo: 'total', titulo: 'Total', numero: true, formato: (v) => <strong>{pesos(v)}</strong> },
          ]} />

          <h3>Gráficos</h3>
          <div className="graficos">
            <GraficoBarras titulo="Facturado por clínica" series={['Atenciones', 'Laboratorio']} formato={pesos}
              datos={filas.map((f) => ({ etiqueta: f.clinica, valores: [f.atenciones, f.laboratorio] }))} />
            <GraficoTorta titulo="Atenciones por tipo" formato={pesos}
              datos={Object.entries(r.por_tipo_atencion).map(([etiqueta, valor]) => ({ etiqueta, valor }))} />
            <GraficoBarrasHorizontal titulo="Laboratorio por estudio" formato={pesos}
              datos={Object.entries(r.laboratorio_por_estudio).map(([etiqueta, valor]) => ({ etiqueta, valor }))} />
          </div>
        </>
      )}
    </>
  )
}
