import { useEffect, useRef, useState } from 'react'
import { fecha } from '../api.js'

// Campo de fecha en formato dd/mm/aaaa: se puede escribir a mano (solo números, las barras
// se agregan solas) o elegir en el calendario con el botón 📅.
// Recibe y devuelve la fecha como 'AAAA-MM-DD'. Opcionales: min y max ('AAAA-MM-DD').
export default function CampoFecha({ valor, onCambio, required, min, max }) {
  const [texto, setTexto] = useState(valor ? fecha(valor) : '')
  const [fueraDeRango, setFueraDeRango] = useState('')
  const ultimoEnviado = useRef(valor)
  const calendario = useRef(null)

  // Si el valor cambia desde afuera (por ejemplo, al limpiar el formulario), se actualiza el texto
  useEffect(() => {
    if (valor !== ultimoEnviado.current) {
      ultimoEnviado.current = valor
      setTexto(valor ? fecha(valor) : '')
    }
  }, [valor])

  function enviar(nuevo) {
    // Fechas fuera del rango permitido (por ejemplo, futuras en un filtro) no se aplican
    let motivo = ''
    if (nuevo && max && nuevo > max) motivo = `No puede ser posterior al ${fecha(max)}`
    if (nuevo && min && nuevo < min) motivo = `No puede ser anterior al ${fecha(min)}`
    setFueraDeRango(motivo)
    if (motivo) nuevo = ''
    ultimoEnviado.current = nuevo
    onCambio(nuevo)
  }

  function escribir(e) {
    const numeros = e.target.value.replace(/\D/g, '').slice(0, 8)
    let formateado = numeros
    if (numeros.length > 4) formateado = `${numeros.slice(0, 2)}/${numeros.slice(2, 4)}/${numeros.slice(4)}`
    else if (numeros.length > 2) formateado = `${numeros.slice(0, 2)}/${numeros.slice(2)}`
    setTexto(formateado)

    if (numeros.length === 8) {
      const dia = numeros.slice(0, 2), mes = numeros.slice(2, 4), anio = numeros.slice(4)
      const d = new Date(`${anio}-${mes}-${dia}T00:00`)
      const valida = !isNaN(d) && d.getDate() === Number(dia) && d.getMonth() + 1 === Number(mes)
      enviar(valida ? `${anio}-${mes}-${dia}` : '')
    } else {
      enviar('')
    }
  }

  // Fecha elegida en el calendario del navegador (ya viene como AAAA-MM-DD)
  function elegir(e) {
    if (!e.target.value) return
    setTexto(fecha(e.target.value))
    enviar(e.target.value)
  }

  function abrirCalendario() {
    try {
      calendario.current.showPicker()
    } catch {
      calendario.current.click()
    }
  }

  return (
    <span className="campo-fecha">
      <input value={texto} onChange={escribir} placeholder="dd/mm/aaaa" inputMode="numeric"
        pattern="\d{2}/\d{2}/\d{4}" title={fueraDeRango || 'Fecha en formato dd/mm/aaaa'} required={required}
        className={'fecha' + (fueraDeRango ? ' fuera-de-rango' : '')} />
      <button type="button" className="secundario calendario" onClick={abrirCalendario} title="Elegir en el calendario">📅</button>
      <input ref={calendario} type="date" value={valor || ''} min={min} max={max} onChange={elegir}
        className="calendario-oculto" tabIndex={-1} aria-hidden="true" />
      {fueraDeRango && <small className="error">{fueraDeRango}</small>}
    </span>
  )
}
