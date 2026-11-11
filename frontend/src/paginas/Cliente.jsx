import { useEffect, useState } from 'react'
import { api, fecha, fechaHora, hoy } from '../api.js'

// Vista de solo lectura: el cliente ve sus mascotas, su historia clínica y sus análisis
export default function Cliente({ usuario }) {
  const [mascotas, setMascotas] = useState([])
  const [avisos, setAvisos] = useState([])

  useEffect(() => {
    api.get(`/clientes/${usuario.dni}/mascotas`).then(setMascotas)
    api.get(`/clientes/${usuario.dni}/avisos`).then(setAvisos)
  }, [])

  return (
    <>
      {avisos.length > 0 && (
        <div className="tarjeta avisos-cliente">
          <h3>Mis avisos</h3>
          {avisos.map((a) => (
            <p key={a.id}><span className="ayuda">{fechaHora(a.fecha)} · {a.canal}</span><br />{a.mensaje}</p>
          ))}
        </div>
      )}

      <h2>Mis mascotas</h2>
      {mascotas.length === 0 && <p>No tenés mascotas registradas.</p>}
      {mascotas.map((m) => (
        <div key={m.id_mascota} className="tarjeta">
          <h3>{m.nombre}</h3>
          <p>{m.especie} - {m.raza} | Nacimiento: {fecha(m.fecha_nacimiento)} | Peso: {m.peso} kg</p>

          <h4>Vacunas</h4>
          <ul>
            {m.vacunas.map((v, i) => (
              <li key={i}>{v.nombre} - aplicada {fecha(v.fecha)}, {v.vence < hoy() ? <span className="alerta">vencida</span> : `vigente hasta ${fecha(v.vence)}`}</li>
            ))}
          </ul>
          {m.vacunas_pendientes.length > 0
            ? <p className="alerta">Vacunas obligatorias pendientes: {m.vacunas_pendientes.join(', ')}</p>
            : <p>Vacunas obligatorias al día.</p>}

          <h4>Historia clínica</h4>
          {m.historia_clinica.length === 0 && <p>Sin atenciones registradas.</p>}
          {m.historia_clinica.map((c) => (
            <div key={c.id_consulta} className="orden">
              <strong>{fechaHora(c.fecha_hora)} - {c.tipo_atencion}</strong> con {c.veterinario} ({c.clinica})
              <p>Motivo: {c.motivo}</p>
              {c.diagnostico && <p>Diagnóstico: {c.diagnostico} | Tratamiento: {c.tratamiento}</p>}
              {c.ordenes.map((o) => (
                <div key={o.id_orden}>
                  Análisis: {o.tipo_estudio}
                  <ul>
                    {o.muestras.map((mu) => (
                      <li key={mu.codigo}>
                        {mu.tipo}{mu.reextraccion_de && ' (nueva extracción)'}: <span className="estado">{mu.estado}</span>
                        {mu.motivo_rechazo && <span className="alerta"> {mu.motivo_rechazo.split(': ').pop()}</span>}
                        {mu.reemplazada_por && ' - se volvió a extraer'}
                        {mu.resultado && <> - <span className="multilinea">{mu.resultado.informe}</span></>}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          ))}
        </div>
      ))}
    </>
  )
}
