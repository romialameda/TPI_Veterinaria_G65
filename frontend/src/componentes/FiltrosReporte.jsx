import CampoFecha from './CampoFecha.jsx'
import { hoy } from '../api.js'

// Barra de filtros de un reporte.
// filtros: [{ nombre, etiqueta, tipo: 'fecha' | 'select' | 'texto' | 'check', opciones?: [{ valor, texto }] }]
// valores: { nombre: valor }. Cada cambio se aplica enseguida (onCambio) y afecta a TODO el reporte:
// indicadores, tablas y gráficos. Las fechas no pueden ser futuras y "hasta" no puede ser anterior a "desde".
export default function FiltrosReporte({ filtros, valores, onCambio }) {
  const cambiar = (nombre, valor) => onCambio({ ...valores, [nombre]: valor })
  const hayFiltros = Object.values(valores).some((v) => v !== '' && v !== false)

  return (
    <div className="filtros tarjeta">
      {filtros.map((f) => (
        <label key={f.nombre} className={f.tipo === 'check' ? 'check' : ''}>
          {f.tipo === 'check' ? (
            <><input type="checkbox" checked={!!valores[f.nombre]} onChange={(e) => cambiar(f.nombre, e.target.checked)} />{f.etiqueta}</>
          ) : (
            <>
              {f.etiqueta}
              {f.tipo === 'fecha' && (
                <CampoFecha valor={valores[f.nombre]} onCambio={(v) => cambiar(f.nombre, v)} max={hoy()}
                  min={f.nombre === 'hasta' && valores.desde ? valores.desde : undefined} />
              )}
              {f.tipo === 'texto' && <input value={valores[f.nombre]} placeholder={f.ayuda} onChange={(e) => cambiar(f.nombre, e.target.value)} />}
              {f.tipo === 'select' && (
                <select value={valores[f.nombre]} onChange={(e) => cambiar(f.nombre, e.target.value)}>
                  <option value="">Todos</option>
                  {f.opciones.map((o) => <option key={o.valor} value={o.valor}>{o.texto}</option>)}
                </select>
              )}
            </>
          )}
        </label>
      ))}
      {hayFiltros && (
        <button type="button" className="secundario" onClick={() => onCambio(Object.fromEntries(filtros.map((f) => [f.nombre, f.tipo === 'check' ? false : ''])))}>
          Limpiar filtros
        </button>
      )}
    </div>
  )
}

// Arma la parte "?clave=valor&..." de la URL, sin los filtros vacíos
export function consulta(valores) {
  const partes = Object.entries(valores)
    .filter(([, v]) => v !== '' && v !== false && v != null)
    .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
  return partes.length ? '?' + partes.join('&') : ''
}
