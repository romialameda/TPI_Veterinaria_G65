import { Link } from 'react-router-dom'
import { REPORTES } from './comun.jsx'

export default function MenuReportes() {
  return (
    <>
      <h2>Reportes</h2>
      <div className="menu-reportes">
        {REPORTES.map((r, i) => (
          <Link key={r.ruta} to={`/secretario/reportes/${r.ruta}`} className="tarjeta opcion-reporte">
            <span className="numero-reporte">{i + 1}</span>
            <strong>{r.titulo}</strong>
            <p>{r.descripcion}</p>
          </Link>
        ))}
      </div>
    </>
  )
}
