import { useState } from 'react'
import { Routes, Route, Navigate, NavLink } from 'react-router-dom'
import Login from './paginas/Login.jsx'
import Clientes from './paginas/secretario/Clientes.jsx'
import Turnos from './paginas/secretario/Turnos.jsx'
import Logistica from './paginas/secretario/Logistica.jsx'
import Comprobantes from './paginas/secretario/Comprobantes.jsx'
import Reportes from './paginas/secretario/Reportes.jsx'
import Veterinario from './paginas/Veterinario.jsx'
import Bioquimico from './paginas/Bioquimico.jsx'
import Cliente from './paginas/Cliente.jsx'

// Página de inicio de cada rol
const INICIO = {
  Secretario: '/secretario/clientes',
  Veterinario: '/veterinario',
  'Bioquímico': '/bioquimico',
  Cliente: '/cliente',
}

export default function App() {
  // El usuario logueado se guarda en el navegador para no perderlo al recargar la página
  const [usuario, setUsuario] = useState(() => JSON.parse(localStorage.getItem('usuario') || 'null'))

  function entrar(datos) {
    localStorage.setItem('usuario', JSON.stringify(datos))
    setUsuario(datos)
  }

  function salir() {
    localStorage.removeItem('usuario')
    setUsuario(null)
  }

  if (!usuario) {
    return (
      <Routes>
        <Route path="/login" element={<Login onEntrar={entrar} />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    )
  }

  return (
    <>
      <header className="encabezado">
        <strong>Veterinaria</strong>
        {usuario.rol === 'Secretario' && (
          <nav>
            <NavLink to="/secretario/clientes">Clientes y mascotas</NavLink>
            <NavLink to="/secretario/turnos">Turnos</NavLink>
            <NavLink to="/secretario/logistica">Logística</NavLink>
            <NavLink to="/secretario/comprobantes">Comprobantes</NavLink>
            <NavLink to="/secretario/reportes">Reportes</NavLink>
          </nav>
        )}
        <span className="usuario">
          {usuario.nombre} ({usuario.rol}) <button onClick={salir}>Salir</button>
        </span>
      </header>

      <main>
        <Routes>
          {usuario.rol === 'Secretario' && (
            <>
              <Route path="/secretario/clientes" element={<Clientes />} />
              <Route path="/secretario/turnos" element={<Turnos />} />
              <Route path="/secretario/logistica" element={<Logistica />} />
              <Route path="/secretario/comprobantes" element={<Comprobantes />} />
              <Route path="/secretario/reportes" element={<Reportes />} />
            </>
          )}
          {usuario.rol === 'Veterinario' && <Route path="/veterinario" element={<Veterinario usuario={usuario} />} />}
          {usuario.rol === 'Bioquímico' && <Route path="/bioquimico" element={<Bioquimico usuario={usuario} />} />}
          {usuario.rol === 'Cliente' && <Route path="/cliente" element={<Cliente usuario={usuario} />} />}
          <Route path="*" element={<Navigate to={INICIO[usuario.rol]} />} />
        </Routes>
      </main>
    </>
  )
}
