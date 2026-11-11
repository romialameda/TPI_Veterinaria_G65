# Sistema de Red de Clínicas Veterinarias y Derivación de Laboratorio

Trabajo Práctico Integrador 2026 (Tema 2) de la cátedra **Desarrollo de Aplicaciones con Objetos (DAO)** — Ingeniería en Sistemas de Información.

---

## Descripción del Proyecto

El sistema modela la operatoria de una red de clínicas veterinarias conectadas con un laboratorio central de diagnóstico. Cubre la atención clínica del paciente, la agenda de turnos, la emisión de órdenes de derivación, la logística y cadena de custodia de muestras biológicas, la recepción con verificación del precinto sanitario, la carga de resultados, la emisión de comprobantes y la generación de reportes gerenciales.

---

## Cómo iniciar el proyecto

### Requisitos

- **Python 3.10 o superior**
- **Node.js** (versión LTS) → instalador `.msi` de https://nodejs.org/ (después de instalarlo, reiniciar PyCharm)

### 1. Instalar dependencias (solo la primera vez)

Desde la carpeta del proyecto, con el entorno virtual `.venv` activo:

```bash
# Backend (FastAPI y Uvicorn)
pip install -r backend/requirements.txt

# Frontend (React, React Router y Vite)
cd frontend
npm install
cd ..
```

> En redes con proxy (por ejemplo, de una empresa) pip y npm pueden tardar varios minutos o quedar colgados. Si pasa, conviene instalar desde otra red.

### 2. Iniciar la aplicación (dos terminales)

**Terminal 1 — API (backend):**

```bash
cd backend
uvicorn api.app:app --reload
```

Queda en http://localhost:8000. En http://localhost:8000/docs se pueden probar todos los endpoints sin el front.

**Terminal 2 — Front:**

```bash
cd frontend
npm run dev
```

Abrir **http://localhost:5173** en el navegador. Las dos terminales tienen que quedar abiertas mientras se usa la aplicación.

La primera vez, la API crea la base `backend/veterinaria.db` y la completa con datos de prueba:

- `backend/db/datos_ejemplo.sql`: sedes, laboratorio, profesionales, conservadoras y usuarios.
- `backend/db/datos_demo.py`: clientes, mascotas, vacunas (al día, vencidas y faltantes), turnos para hoy y mañana, atenciones de los días anteriores y muestras en todos los estados (resultado listo, rechazada y re-extraída, en tránsito esperando recepción, recibida esperando análisis y extraída esperando remito). Las fechas se calculan a partir del día en que se crea la base.

Para volver a los datos de prueba: detener la API, borrar `backend/veterinaria.db` y volver a iniciarla (se pierde lo cargado a mano).

### 3. Usuarios de prueba

| Usuario | Contraseña | Rol | Quién es |
|---|---|---|---|
| `secretario` | `1234` | Secretario | Recepción |
| `mlopez` | `1234` | Veterinario | Mariana López — Sede Centro, turno mañana (09:00 a 13:00) |
| `sherrera` | `1234` | Veterinario | Sofía Herrera — Sede Centro, turno tarde (16:00 a 20:00) |
| `egomez` | `1234` | Veterinario | Esteban Gómez — Sede Norte, turno mañana (09:00 a 13:00) |
| `pacosta` | `1234` | Veterinario | Pablo Acosta — Sede Norte, turno tarde (16:00 a 20:00) |
| `ctevez` | `1234` | Bioquímico | Carlos Tevez — Laboratorio Central |
| `35890123` | `1234` | Cliente | Laura Fernández — dueña de Simón (perro) y Mora (gata) |
| `40111222` | `1234` | Cliente | Martín Ruiz — dueño de Rocco (perro) |
| `33222111` | `1234` | Cliente | Ana Pérez — dueña de Luna (gata) y Toby (perro) |

Los clientes que crea el secretario ingresan con su **DNI** como usuario y la contraseña que se cargó en el alta.

Login simple: usuario y contraseña en texto plano comparados contra la tabla `usuario` (simplificación del TP, sin cifrado ni tokens). El front muestra solo las pantallas del rol que ingresó.

### Demo por consola (sin front)

Requiere Python 3.10 o superior, sin dependencias externas. La demo borra y recrea `demo_veterinaria.db` en cada ejecución; al final cierra la conexión y vuelve a leer todo de la base para mostrar que los datos persisten.

```bash
cd backend
python main.py
```

---

## Arquitectura y Patrones de Diseño

El sistema se organiza en capas:

- **`models/`**: entidades del dominio y sus reglas de negocio. No saben que existe una base de datos.
- **`services/`**: casos de uso (uno por grupo de procesos de la consigna). Es lo que va a invocar el front.
- **`dao/`**: un DAO por entidad; es el único lugar donde se escribe SQL.
- **`db/`**: conexión a SQLite, script de tablas y el repositorio que reconstruye los objetos al iniciar.
- **`Reports/`**: reportes estadísticos.

### 1. Patrón State: ciclo de vida de la muestra biológica
Cada estado sabe qué transiciones admite; las inválidas lanzan `ValueError` sin `if/elif` anidados.

`Extraída` → `Empaquetada` → `En tránsito` → `Recibida` → `Analizada`. Una muestra pasa a `Rechazada`:
- desde `En tránsito`, si el precinto llega roto (se rechaza todo el contenedor) o si el bioquímico la rechaza puntualmente al recibir (recipiente roto, hemolizada, volumen insuficiente, mal rotulada...);
- desde `Recibida`, si el problema se detecta en el laboratorio antes de analizarla.

`Rechazada` y `Analizada` son estados finales; una muestra rechazada se puede volver a extraer (queda vinculada a la original).

### 2. Patrón State: ciclo de vida del remito biológico
El remito coordina a sus muestras: cada transición del remito dispara la de todas sus muestras.

`En preparación` → `En tránsito` → `Recibido`, o bien `Rechazado` si en la recepción el bioquímico informa el precinto violado. Si el precinto llegó intacto pero se rechazó alguna muestra puntual, el remito queda `Recibido` **con observaciones**. Solo se pueden agregar muestras en preparación, solo se registran eventos de traslado en tránsito y un remito no se puede recibir dos veces.

### 3. Patrón Observer: persistencia y avisos
Hay **dos sujetos observables**, cada uno con sus observadores:

- **`MuestraBiologica`** avisa en cada cambio de estado a:
  - **`PersistidorMuestra`**: guarda el nuevo estado y la trazabilidad en la base.
  - **`NotificadorCliente`**: avisa al responsable de la mascota cuando todos los resultados de una orden están listos o cuando una muestra se rechaza.
  - **`AvisoClinicaMuestra`**: avisa a la recepción de la clínica cuando el laboratorio rechaza una muestra que ya había recibido, con la mascota, el responsable (y su teléfono) y el veterinario.
- **`RemitoBiologico`** avisa en cada cambio de estado a:
  - **`AvisoClinica`**: avisa a la clínica de origen si el remito llegó con el precinto roto o se recibió con muestras rechazadas, indicando por cada muestra la mascota, el responsable (y su teléfono) y el veterinario. La recepción lo ve en **Avisos → Para las clínicas**.

El envío de los avisos es **simulado** (no se integra un servicio real de email o WhatsApp): cada aviso se guarda en la tabla `notificacion` y el destinatario lo ve en el sistema (**Mis avisos** para el cliente, **Avisos** para recepción). Ni la muestra ni el remito saben quién los observa: se pueden sumar observadores sin modificarlos.

### 4. Patrón Singleton: conexión a la base de datos
`Conexion()` devuelve siempre la misma instancia, así toda la aplicación comparte una única conexión a SQLite.

### 5. Patrón DAO: acceso a datos
Cada entidad tiene su DAO (`ClienteDAO`, `MuestraDAO`, `RemitoDAO`…) con los métodos para insertar, actualizar y leer. Los servicios usan los DAOs y nunca escriben SQL.

---

## Base de datos

- Motor: **SQLite** (incluido en Python, no requiere instalación). El archivo `veterinaria.db` se crea solo la primera vez, a partir de `db/schema.sql` y `db/datos_iniciales.sql`.
- Al iniciar, `Repositorio.cargar()` lee todas las tablas y arma los objetos con sus relaciones. Después, cada operación de un servicio se guarda en la base dentro de una transacción.
- Los cambios de estado de las muestras se guardan mediante un observador más (`PersistidorMuestra`), sin que `MuestraBiologica` conozca la base.
- Los estados (State) se guardan como texto (`'En tránsito'`) y se reconstruyen con los diccionarios `ESTADOS_MUESTRA` y `ESTADOS_REMITO`.
- Los números internos (consultas, órdenes, remitos, turnos, resultados, comprobantes) son autogenerados por la base.

---

## Procesos de negocio cubiertos

| Proceso | Dónde |
|---|---|
| 1. Administrar clientes | `ServicioClientes` (alta, búsqueda, modificación, baja) |
| 2. Mascotas e historias clínicas | `ServicioClientes` (alta, modificación, baja lógica, vacunas, historia clínica) |
| 3. Consultas y órdenes de derivación | `ServicioAtencion` (turnos, consultas, órdenes) |
| 4. Empaquetado con remito y precinto | `ServicioLaboratorio.empaquetar` |
| 5. Cadena de envío | `ServicioLaboratorio.despachar` / `registrar_evento_traslado` |
| 6. Recepción verificando el precinto | `ServicioLaboratorio.recibir_remito` |
| 7. Resultados y comprobantes | `ServicioLaboratorio.registrar_resultado` / `ServicioAtencion.emitir_comprobante` |

## Validaciones de negocio

- Toda mascota debe tener un responsable asociado.
- Si el precinto llega roto, el remito y sus muestras pasan a `Rechazado`/`Rechazada` y no se pueden analizar.
- Trazabilidad de estados de la muestra con fecha, hora y motivo.
- Un veterinario no puede tener turnos superpuestos, ni turnos fuera de su horario (Mañana 09:00 a 13:00 / Tarde 16:00 a 20:00).
- No se pueden agendar turnos en fechas u horas pasadas. La duración depende del tipo: Consulta 45 min, Control 30 min (límite 30 a 90).
- Solo se pueden registrar vacunas del catálogo de la especie (`vacuna_catalogo`). Cada vacuna es vigente por 1 año: no se puede repetir mientras esté vigente y, al vencer, vuelve a figurar como pendiente.
- Un turno se atiende solo el día del turno (a cualquier hora de ese día). Las urgencias las registra recepción (sin turno, con precio de urgencia) y el veterinario las atiende desde "Urgencias de hoy".
- Al registrar una atención se controla el esquema de vacunas obligatorias de la especie (`EsquemaVacunacion`).
- Una conservadora no puede estar en dos remitos a la vez ni superar su capacidad.

## Reportes

En el front, **Reportes** abre un menú con los cinco reportes; cada uno tiene su página (con pestañas para pasar de uno a otro) con filtros arriba, y debajo indicadores, tablas y gráficos. **Los filtros se aplican a toda la página** (indicadores, tablas y gráficos). Las fechas de los filtros no pueden ser futuras y "hasta" no puede ser anterior a "desde". En la API cada reporte tiene su endpoint (`/reportes/atenciones`, `/reportes/rechazadas`, `/reportes/facturacion`, `/reportes/tiempos`, `/reportes/turnos`) y las opciones de los filtros salen de `/reportes/opciones`.

| Reporte | Filtros |
|---|---|
| 1. Atenciones clínicas y derivaciones | Fechas, clínica, veterinario, responsable, paciente (de ese responsable), especie, tipo de atención |
| 2. Muestras rechazadas (precinto roto o rechazo puntual, por causa) | Fechas, clínica, veterinario, especie, conservadora (en la API también se puede ordenar) |
| 3. Facturación por clínica y servicios de laboratorio | Fechas, clínica, veterinario |
| 4. Tiempos y demoras (tránsito, procesamiento y demora total por estudio) | Fechas, clínica, estudio, tipo de muestra |
| 5. Turnos y asistencia (atendidos, ausentes, cancelados, pendientes; urgencias sin turno) | Fechas, sede, veterinario, tipo de turno, estado |

- **Facturación:** lo cobrado a los clientes, desglosado en atenciones (precio fijo según el tipo) y servicios de laboratorio (arancel fijo por muestra analizada).
- **Tiempos:** el tránsito es solo de ida (las muestras no vuelven); el procesamiento va de la recepción al resultado; la demora total va de la extracción al resultado y sirve para informarle al cliente cuánto va a tardar cada estudio.

## Precios

Los precios están en `backend/models/clinica/Tarifario.py`: Control (30 min) $12.000, Consulta (45 min) $18.000, Urgencia (sin turno) $30.000, y $4.500 por cada muestra analizada. El precio se informa al dar el turno y se aplica solo al registrar la atención: el veterinario no lo carga a mano.

## Validaciones de datos de entrada

Se validan en el modelo (`models/Validaciones.py`) y además en los formularios del front:

- DNI: 7 u 8 números, sin letras ni puntos. Nombre y apellido: solo letras.
- Teléfono: números, espacios o guiones (mínimo 7 números). Email: formato válido (opcional).
- Mascota: nombre obligatorio, peso entre 0,1 y 150 kg, fecha de nacimiento no futura.
- Atención y turno: motivo obligatorio.
- Traslado: ubicación obligatoria, novedad de una lista (Sin novedad, Demora, Golpe, Conservadora dañada, Cadena de frío interrumpida, Otro; si es "Otro", la observación es obligatoria), transportista obligatorio al despachar.
- Resultado de análisis: el bioquímico lo escribe como texto libre (obligatorio, hasta 3000 caracteres). Contraseña: mínimo 4 caracteres.

---

## Estructura del Repositorio

```text
TPI_Veterinaria_G65/
├── backend/                            (código Python: se ejecuta desde esta carpeta)
│   ├── models/
│   │   ├── Usuario.py
│   │   ├── clinica/                    Persona (abstracta), Cliente, Veterinario, Clinica, Mascota,
│   │   │                               Vacuna, EsquemaVacunacion, Turno, ConsultaMedica, ComprobanteAtencion
│   │   ├── Laboratorio/                Laboratorio, Bioquimico, OrdenDerivacion, MuestraBiologica,
│   │   │                               EstadoMuestra (State), ObserverMuestra (Observer), ResultadoAnalisis
│   │   └── Logistica/                  Conservadora, PrecintoSanitario, RemitoBiologico,
│   │                                   EstadoRemito (State), EventoTraslado
│   ├── services/                       ServicioClientes, ServicioAtencion, ServicioLaboratorio, ServicioUsuarios
│   ├── dao/                            un DAO por entidad + PersistidorMuestra (Observer)
│   ├── db/                             schema.sql, datos_iniciales.sql, datos_ejemplo.sql,
│   │                                   Conexion (Singleton), Repositorio, fechas
│   ├── Reports/                        GeneradorReportes
│   ├── api/                            app.py (FastAPI), convertir.py (objetos -> JSON)
│   ├── main.py                         demo completa por consola (usa demo_veterinaria.db)
│   └── requirements.txt
├── frontend/                           React + Vite
│   └── src/
│       ├── App.jsx                     rutas por rol
│       ├── api.js                      llamadas a la API
│       └── paginas/                    Login, secretario/, Veterinario, Bioquimico, Cliente
└── README.md
```
