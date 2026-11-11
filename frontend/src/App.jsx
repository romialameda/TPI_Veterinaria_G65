import { useState } from 'react'
import { Routes, Route, Navigate, NavLink } from 'react-router-dom'
import Login from './paginas/Login.jsx'
import Logo from './componentes/Logo.jsx'
import Clientes from './paginas/secretario/Clientes.jsx'
import Turnos from './paginas/secretario/Turnos.jsx'
import Logistica from './paginas/secretario/Logistica.jsx'
import Comprobantes from './paginas/secretario/Comprobantes.jsx'
import Avisos from './paginas/secretario/Avisos.jsx'
import ReporteTurnos from './paginas/secretario/reportes/ReporteTurnos.jsx'
import MenuReportes from './paginas/secretario/reportes/MenuReportes.jsx'
import ReporteAtenciones from './paginas/secretario/reportes/ReporteAtenciones.jsx'
import ReporteRechazadas from './paginas/secretario/reportes/ReporteRechazadas.jsx'
import ReporteFacturacion from './paginas/secretario/reportes/ReporteFacturacion.jsx'
import ReporteTiempos from './paginas/secretario/reportes/ReporteTiempos.jsx'
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
        <span className="marca"><Logo tamano={38} /><span><strong>Huellitas</strong><small>Red veterinaria</small></span></span>
        {usuario.rol === 'Secretario' && (
          <nav>
            <NavLink to="/secretario/clientes">Clientes y mascotas</NavLink>
            <NavLink to="/secretario/turnos">Turnos</NavLink>
            <NavLink to="/secretario/logistica">Logística</NavLink>
            <NavLink to="/secretario/comprobantes">Comprobantes</NavLink>
            <NavLink to="/secretario/avisos">Avisos</NavLink>
            <NavLink to="/secretario/reportes">Reportes</NavLink>
          </nav>
        )}
        <span className="usuario">
          <span className="avatar">{usuario.nombre.charAt(0)}</span>
          <span>{usuario.nombre}<small>{usuario.rol}</small></span>
          <button onClick={salir}>Salir</button>
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
              <Route path="/secretario/avisos" element={<Avisos />} />
              <Route path="/secretario/reportes/turnos" element={<ReporteTurnos />} />
              <Route path="/secretario/reportes" element={<MenuReportes />} />
              <Route path="/secretario/reportes/atenciones" element={<ReporteAtenciones />} />
              <Route path="/secretario/reportes/rechazadas" element={<ReporteRechazadas />} />
              <Route path="/secretario/reportes/facturacion" element={<ReporteFacturacion />} />
              <Route path="/secretario/reportes/tiempos" element={<ReporteTiempos />} />
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
