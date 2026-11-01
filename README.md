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

`Extraída` → `Empaquetada` → `En tránsito` → `Recibida` → `Analizada`, o bien `En tránsito` → `Rechazada` si el precinto llega roto. `Rechazada` y `Analizada` son estados finales.

### 2. Patrón State: ciclo de vida del remito biológico
El remito coordina a sus muestras: cada transición del remito dispara la de todas sus muestras.

`En preparación` → `En tránsito` → `Recibido`, o bien `Rechazado` si en la recepción el bioquímico informa el precinto violado. Solo se pueden agregar muestras en preparación, solo se registran eventos de traslado en tránsito y un remito no se puede recibir dos veces.

### 3. Patrón Observer: auditoría y notificaciones
Desacopla `MuestraBiologica` de las acciones derivadas de sus cambios de estado:
- **`AuditorTrazabilidad`**: registra cada transición en una bitácora.
- **`NotificadorCliente`**: avisa por WhatsApp si una muestra es rechazada (para coordinar la nueva extracción) y por email cuando **todas** las muestras vigentes de la orden fueron analizadas.

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
- Un turno se atiende solo el día del turno (a cualquier hora de ese día). Las urgencias se registran sin turno.
- Al registrar una atención se controla el esquema de vacunas obligatorias de la especie (`EsquemaVacunacion`).
- Una conservadora no puede estar en dos remitos a la vez ni superar su capacidad.

## Reportes

1. Atenciones clínicas y derivaciones por clínica y tipo de atención.
2. Muestras rechazadas por fallas en el transporte (por clínica y transportista).
3. Tratamientos aplicados y vacunas pendientes por paciente.
4. Facturación desglosada por clínica y servicios de laboratorio.
5. Tiempo promedio de tránsito y de procesamiento de muestras.

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
