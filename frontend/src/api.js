// Funciones para hablar con la API de Python.
// Si la API responde con error, se lanza un Error con el mensaje de la validación.

async function pedir(metodo, url, datos) {
  const respuesta = await fetch('/api' + url, {
    method: metodo,
    headers: { 'Content-Type': 'application/json' },
    body: datos ? JSON.stringify(datos) : undefined,
  })
  const json = await respuesta.json()
  if (!respuesta.ok) {
    const detalle = typeof json.detail === 'string' ? json.detail : 'Datos inválidos: revisá el formulario.'
    throw new Error(detalle)
  }
  return json
}

export const api = {
  get: (url) => pedir('GET', url),
  post: (url, datos) => pedir('POST', url, datos),
  put: (url, datos) => pedir('PUT', url, datos),
}

// Formatos para mostrar fechas (día/mes/año), horas (00:00 a 23:59) y montos
const dosDigitos = (n) => String(n).padStart(2, '0')

export function fecha(texto) {
  if (!texto) return '-'
  const [anio, mes, dia] = texto.slice(0, 10).split('-')
  return `${dia}/${mes}/${anio}`
}

export function hora(texto) {
  return texto ? texto.slice(11, 16) : '-'
}

export function fechaHora(texto) {
  return texto ? `${fecha(texto)} ${hora(texto)}` : '-'
}

export function pesos(numero) {
  return '$' + Number(numero).toLocaleString('es-AR', { minimumFractionDigits: 2 })
}

// Fecha de hoy en formato AAAA-MM-DD (el que usa la API)
export function hoy() {
  const d = new Date()
  return `${d.getFullYear()}-${dosDigitos(d.getMonth() + 1)}-${dosDigitos(d.getDate())}`
}
