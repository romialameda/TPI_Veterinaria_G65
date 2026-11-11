import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './estilos.css'

// Los campos inválidos se marcan en rojo solo cuando se intenta guardar un formulario con errores.
// Si se guarda bien, la marca se borra (así los campos limpios no quedan en rojo).
document.addEventListener('invalid', (e) => e.target.form?.classList.add('intentado'), true)
document.addEventListener('submit', (e) => e.target.classList.remove('intentado'), true)

createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
)
