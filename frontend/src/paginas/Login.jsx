import { useState } from 'react'
import { api } from '../api.js'

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
      <h1>Veterinaria</h1>
      <form onSubmit={enviar} className="tarjeta">
        <label>Usuario <input value={usuario} onChange={(e) => setUsuario(e.target.value)} required /></label>
        <label>Contraseña <input type="password" value={contrasena} onChange={(e) => setContrasena(e.target.value)} required /></label>
        <button type="submit">Ingresar</button>
        {error && <p className="error">{error}</p>}
      </form>
      <p className="ayuda">
        Usuarios de prueba (contraseña 1234): secretario, mlopez, egomez (veterinarios), ctevez (bioquímico), 35890123 (cliente)
      </p>
    </div>
  )
}
