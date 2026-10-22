# Red de clínicas veterinarias y derivación de laboratorio

Modelo de dominio en Python para clientes, mascotas, atenciones clínicas y el circuito
trazable de derivación de muestras al laboratorio central.

## Alcance actual

El proyecto implementa las entidades y reglas de negocio del flujo clínico y de laboratorio.
Incluye registro de la cadena de custodia, verificación del precinto y evaluación de viabilidad
por temperatura y vencimiento de la muestra. No incluye interfaz de usuario, almacenamiento
persistente, autenticación ni integración con sistemas externos.

Los requisitos funcionales, casos de uso y el modelo de dominio están documentados en
[docs/Requisitos-y-casos-de-uso.md](docs/Requisitos-y-casos-de-uso.md).

## Ejecutar pruebas

Desde la raíz del repositorio:

```powershell
python -m unittest discover -s tests -v
```

## Ejemplo breve

```python
from Models.Clinica import AtencionMedica, Cliente, Mascota
from Models.laboratorio import OrdenDerivacion

cliente = Cliente("cli-1", "Ana Pérez", "555-0101")
mascota = Mascota("mas-1", "Luna", "felino", cliente.id)
cliente.registrar_mascota(mascota)

atencion = AtencionMedica("ate-1", mascota.id, "Dra. Ruiz", "Control")
mascota.registrar_atencion(atencion)
orden = OrdenDerivacion("ord-1", atencion.id, "sangre", "Hemograma")
atencion.emitir_derivacion(orden)
```

El armado de un `RemitoBiologico` asocia muestras y órdenes, genera el identificador de
precinto informado y cambia las órdenes a estado empaquetado. Se registra la custodia
mediante `registrar_custodia`, y el laboratorio confirma recepción con
`registrar_recepcion`. El análisis sólo puede emitirse si el remito se recibe viable.