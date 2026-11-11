// Tabla simple de un reporte. Las filas llegan ya filtradas desde la API.
// columnas: [{ campo, titulo, formato?: (valor, fila) => texto, numero?: true }]
export default function Tabla({ columnas, filas, vacio = 'Sin datos para los filtros elegidos.' }) {
  if (!filas.length) return <p className="ayuda">{vacio}</p>

  return (
    <table>
      <thead>
        <tr>{columnas.map((c) => <th key={c.campo} className={c.numero ? 'numero' : ''}>{c.titulo}</th>)}</tr>
      </thead>
      <tbody>
        {filas.map((f, i) => (
          <tr key={i}>
            {columnas.map((c) => (
              <td key={c.campo} className={c.numero ? 'numero' : ''}>{c.formato ? c.formato(f[c.campo], f) : f[c.campo] ?? '-'}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
