// Gráficos simples hechos con SVG (no hace falta instalar ninguna librería).
// Al pasar el mouse sobre una barra o porción se ve su valor.

// Colores fijos por orden de serie, tomados de la paleta de la app (Canyon, Morning Sky, Olive Grove)
// en tonos más intensos para que se distingan bien, también con daltonismo. Ningún gráfico usa más de 3 series.
export const COLORES = ['#D0602F', '#4F7AB8', '#868228']

const formatoNumero = (n) => Number(n).toLocaleString('es-AR', { maximumFractionDigits: 2 })

function Leyenda({ series }) {
  return (
    <div className="leyenda">
      {series.map((s, i) => (
        <span key={s.nombre}><i style={{ background: COLORES[i % COLORES.length] }} />{s.nombre}</span>
      ))}
    </div>
  )
}

// Barras verticales. datos: [{ etiqueta, valores: [n, n...] }], series: ['Atenciones', 'Derivadas']
export function GraficoBarras({ titulo, datos, series = ['Valor'], formato = formatoNumero, alto = 220 }) {
  if (!datos.length) return <SinDatos titulo={titulo} />
  const maximo = Math.max(...datos.flatMap((d) => d.valores), 1)
  const anchoGrupo = Math.max(60, Math.min(110, 440 / datos.length))
  const anchoBarra = Math.min(36, (anchoGrupo - 16) / series.length)
  const margenIzq = 10, margenInf = 40, ancho = margenIzq + datos.length * anchoGrupo
  const escala = (v) => (v / maximo) * (alto - margenInf - 20)

  return (
    <figure className="grafico">
      <figcaption>{titulo}</figcaption>
      {series.length > 1 && <Leyenda series={series.map((nombre) => ({ nombre }))} />}
      <svg viewBox={`0 0 ${ancho} ${alto}`} width="100%" style={{ maxWidth: ancho * 1.2 }} role="img" aria-label={titulo}>
        <line x1={margenIzq} x2={ancho} y1={alto - margenInf} y2={alto - margenInf} stroke="#c9d3d9" />
        {datos.map((d, i) => {
          const x0 = margenIzq + i * anchoGrupo + (anchoGrupo - anchoBarra * series.length - 2 * (series.length - 1)) / 2
          return (
            <g key={d.etiqueta}>
              {d.valores.map((v, j) => {
                const h = escala(v), x = x0 + j * (anchoBarra + 2), y = alto - margenInf - h
                return (
                  <g key={j}>
                    <rect x={x} y={y} width={anchoBarra} height={Math.max(h, 0)} rx="3" fill={COLORES[j % COLORES.length]}>
                      <title>{`${d.etiqueta}${series.length > 1 ? ' - ' + series[j] : ''}: ${formato(v)}`}</title>
                    </rect>
                    <text x={x + anchoBarra / 2} y={y - 4} textAnchor="middle" className="valor">{formato(v)}</text>
                  </g>
                )
              })}
              <text x={margenIzq + i * anchoGrupo + anchoGrupo / 2} y={alto - margenInf + 16} textAnchor="middle" className="etiqueta">
                {d.etiqueta.length > 18 ? d.etiqueta.slice(0, 17) + '…' : d.etiqueta}
                <title>{d.etiqueta}</title>
              </text>
            </g>
          )
        })}
      </svg>
    </figure>
  )
}

// Barras horizontales (para etiquetas largas). datos: [{ etiqueta, valor }]
export function GraficoBarrasHorizontal({ titulo, datos, formato = formatoNumero, color = COLORES[0] }) {
  if (!datos.length) return <SinDatos titulo={titulo} />
  const maximo = Math.max(...datos.map((d) => d.valor), 1)
  const altoFila = 26, anchoEtiqueta = 140, anchoBarras = 170, ancho = anchoEtiqueta + anchoBarras + 80
  return (
    <figure className="grafico">
      <figcaption>{titulo}</figcaption>
      <svg viewBox={`0 0 ${ancho} ${datos.length * altoFila + 6}`} width="100%" style={{ maxWidth: ancho * 1.2 }} role="img" aria-label={titulo}>
        {datos.map((d, i) => {
          const w = (d.valor / maximo) * anchoBarras, y = i * altoFila + 4
          return (
            <g key={d.etiqueta}>
              <text x={anchoEtiqueta - 8} y={y + 14} textAnchor="end" className="etiqueta">
                {d.etiqueta.length > 22 ? d.etiqueta.slice(0, 21) + '…' : d.etiqueta}<title>{d.etiqueta}</title>
              </text>
              <rect x={anchoEtiqueta} y={y} width={Math.max(w, 2)} height={altoFila - 8} rx="3" fill={color}>
                <title>{`${d.etiqueta}: ${formato(d.valor)}`}</title>
              </rect>
              <text x={anchoEtiqueta + Math.max(w, 2) + 6} y={y + 14} className="valor">{formato(d.valor)}</text>
            </g>
          )
        })}
      </svg>
    </figure>
  )
}

// Torta (anillo). datos: [{ etiqueta, valor }]
export function GraficoTorta({ titulo, datos, formato = formatoNumero }) {
  const total = datos.reduce((s, d) => s + d.valor, 0)
  if (!total) return <SinDatos titulo={titulo} />
  const r = 70, grosor = 32, centro = 90
  let angulo = -Math.PI / 2

  return (
    <figure className="grafico">
      <figcaption>{titulo}</figcaption>
      <div className="torta">
        <svg viewBox="0 0 180 180" width="180" height="180" role="img" aria-label={titulo}>
          {datos.map((d, i) => {
            const fraccion = d.valor / total
            const color = COLORES[i % COLORES.length]
            const texto = `${d.etiqueta}: ${formato(d.valor)} (${Math.round(fraccion * 100)}%)`
            if (fraccion >= 0.9999) {
              return <circle key={d.etiqueta} cx={centro} cy={centro} r={r - grosor / 2} fill="none" stroke={color} strokeWidth={grosor}><title>{texto}</title></circle>
            }
            const inicio = angulo, fin = angulo + fraccion * 2 * Math.PI
            angulo = fin
            const punto = (a, radio) => [centro + radio * Math.cos(a), centro + radio * Math.sin(a)]
            const [x1, y1] = punto(inicio, r), [x2, y2] = punto(fin, r)
            const [x3, y3] = punto(fin, r - grosor), [x4, y4] = punto(inicio, r - grosor)
            const grande = fin - inicio > Math.PI ? 1 : 0
            return (
              <path key={d.etiqueta} fill={color} stroke="#fff" strokeWidth="2"
                d={`M${x1},${y1} A${r},${r} 0 ${grande} 1 ${x2},${y2} L${x3},${y3} A${r - grosor},${r - grosor} 0 ${grande} 0 ${x4},${y4} Z`}>
                <title>{texto}</title>
              </path>
            )
          })}
          <text x={centro} y={centro + 6} textAnchor="middle" className="total"
            style={{ fontSize: formato(total).length > 8 ? 13 : 22 }}>{formato(total)}</text>
        </svg>
        <ul className="leyenda-torta">
          {datos.map((d, i) => (
            <li key={d.etiqueta}>
              <i style={{ background: COLORES[i % COLORES.length] }} />
              {d.etiqueta}: <strong>{formato(d.valor)}</strong> ({Math.round((d.valor / total) * 100)}%)
            </li>
          ))}
        </ul>
      </div>
    </figure>
  )
}

function SinDatos({ titulo }) {
  return (
    <figure className="grafico">
      <figcaption>{titulo}</figcaption>
      <p className="ayuda">Sin datos para los filtros elegidos.</p>
    </figure>
  )
}

// Indicador grande con un número (para totales)
export function Indicador({ titulo, valor, detalle }) {
  return (
    <div className="indicador">
      <span>{titulo}</span>
      <strong>{valor}</strong>
      {detalle && <small>{detalle}</small>}
    </div>
  )
}
