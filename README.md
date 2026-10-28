# Sistema de Red de Clínicas Veterinarias y Derivación de Laboratorio

Trabajo Práctico Integrador para la cátedra de **Diseño de Aplicaciones Orientadas a Objetos (DAO)**.

---

## 📌 Descripción del Proyecto

El sistema modela la operatoria integral de una red de clínicas veterinarias conectadas con un laboratorio central de diagnóstico. Cubre la atención clínica del paciente, la emisión de órdenes de derivación, la logística y cadena de custodia de muestras biológicas y la generación de reportes gerenciales para la toma de decisiones.

---

## 🏗️ Arquitectura y Patrones de Diseño

El diseño desacopla responsabilidades aplicando principios SOLID y patrones de diseño de comportamiento:

### 1. Patrón State (Ciclo de Vida de la Muestra Biológica)
Gestiona de forma dinámica las transiciones de estado de cada muestra sin utilizar estructuras condicionales complejas (`if/elif/else` anidados).
* **Estados implementados:** `Extraída` $\rightarrow$ `Empaquetada` $\rightarrow$ `En tránsito` $\rightarrow$ `Recibida` $\rightarrow$ `Analizada` / `Rechazada`.
* **Regla de integridad:** Si un precinto sanitario llega violado o roto, la muestra pasa automáticamente al estado `Rechazada`, bloqueando de forma irreversible cualquier intento de análisis posterior.

### 2. Patrón Observer (Auditoría y Notificaciones)
Desacopla la entidad observable (`MuestraBiologica`) de las consecuencias colaterales derivadas de sus cambios de estado[cite: 2]:
* **`AuditorTrazabilidad`:** Registra cada transición de forma inmutable con marca temporal y motivo para auditorías forenses y seguimiento de cadena de custodia[cite: 2].
* **`NotificadorCliente`:** Gestiona la comunicación con el cliente según las reglas de negocio:
  * Emite un aviso urgente vía WhatsApp si la muestra es rechazada durante el traslado para coordinar una nueva extracción[cite: 2].
  * Emite una notificación por correo únicamente cuando **todas** las muestras asociadas a una orden de derivación completaron su análisis.

---

## 📂 Estructura del Repositorio[cite: 3]

```text
TPI_Veterinaria_G65/
│
├── Models/
│   ├── Clinica/
│   │   ├── Persona.py
│   │   ├── Cliente.py
│   │   ├── Mascota.py
│   │   ├── Consulta.py
│   │   └── Vacuna.py
│   ├── Laboratorio/
│   │   ├── MuestraBiologica.py
│   │   ├── EstadoMuestra.py
│   │   ├── OrdenDerivacion.py
│   │   ├── ResultadoAnalisis.py
│   │   └── ObserverMuestra.py
│   └── Logistica/
│       ├── Conservadora.py
│       ├── PrecintoSanitario.py
│       └── RemitoBiologico.py
│
├── Reportes/
│   └── GeneradorReportes.py
│
├── main.py
└── README.md