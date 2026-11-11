import { useEffect, useState } from 'react'
import { api, fechaHora } from '../../api.js'

// Avisos generados por los observadores (patrón Observer):
// - a las clínicas: muestras rechazadas, con a quién llamar (AvisoClinica y AvisoClinicaMuestra)
// - a los clientes: resultados listos o muestras rechazadas (NotificadorCliente)
export default function Avisos() {
  const [avisos, setAvisos] = useState([])
  const [filtro, setFiltro] = useState('Clínica')

  useEffect(() => { api.get('/avisos').then(setAvisos) }, [])

  const visibles = avisos.filter((a) => a.destinatario_tipo === filtro)

  return (
    <>
      <h2>Avisos</h2>
      <nav className="pestanas">
        <a href="#" className={filtro === 'Clínica' ? 'active' : ''} onClick={(e) => { e.preventDefault(); setFiltro('Clínica') }}>
          Para las clínicas ({avisos.filter((a) => a.destinatario_tipo === 'Clínica').length})
        </a>
        <a href="#" className={filtro === 'Cliente' ? 'active' : ''} onClick={(e) => { e.preventDefault(); setFiltro('Cliente') }}>
          Enviados a clientes ({avisos.filter((a) => a.destinatario_tipo === 'Cliente').length})
        </a>
      </nav>
      <p className="ayuda">
        {filtro === 'Clínica'
          ? 'Muestras que el laboratorio rechazó: avisale al responsable y al veterinario para coordinar una nueva extracción.'
          : 'Avisos que el sistema le mandó a cada cliente (envío simulado por email o WhatsApp).'}
      </p>
      {visibles.length === 0 && <p>No hay avisos.</p>}
      {visibles.map((a) => (
        <div key={a.id} className="tarjeta aviso-item">
          <div className="fila">
            <strong>{a.destinatario}</strong>
            <span className="estado">{a.canal}</span>
            <span className="ayuda derecha">{fechaHora(a.fecha)}</span>
          </div>
          <p className="multilinea">{a.mensaje}</p>
        </div>
      ))}
    </>
  )
}
