// Campo para escribir un monto a mano (sin las flechitas de los campos numéricos).
// Acepta números con coma o punto decimal: "15000" o "15000,50".
export default function CampoImporte({ valor, onCambio, placeholder = '$', required }) {
  function escribir(e) {
    const texto = e.target.value.replace(',', '.')
    if (/^\d*\.?\d{0,2}$/.test(texto)) onCambio(texto)
  }

  return (
    <input value={valor} onChange={escribir} placeholder={placeholder} inputMode="decimal"
      required={required} className="importe" />
  )
}
