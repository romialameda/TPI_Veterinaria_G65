import { useState } from 'react'
import { api } from '../api.js'
import Logo from '../componentes/Logo.jsx'

export default function Login({ onEntrar }) {
  const [usuario, setUsuario] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [error, setError] = useState('')

  async function enviar(e) {
    e.preventDefault()
    try {
      onEntrar(await api.post('/login', { usuario, contrasena }))
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="login">
      <form onSubmit={enviar} className="tarjeta">
        <div className="login-marca">
          <Logo tamano={84} />
          <h1>Huellitas</h1>
          <p>Red de clínicas veterinarias y laboratorio</p>
        </div>
        <label>Usuario <input value={usuario} onChange={(e) => setUsuario(e.target.value)} required /></label>
        <label>Contraseña <input type="password" value={contrasena} onChange={(e) => setContrasena(e.target.value)} required /></label>
        <button type="submit">Ingresar</button>
        {error && <p className="error">{error}</p>}
      </form>
      <p className="ayuda">
        Usuarios de prueba (contraseña 1234): secretario · mlopez, sherrera, egomez, pacosta (veterinarios) · ctevez (bioquímico) · 35890123, 40111222, 33222111 (clientes)
      </p>
    </div>
  )
}
