-- =====================================================================
-- Esquema de la base de datos (SQLite)
-- Fechas: texto ISO 'AAAA-MM-DD HH:MM:SS'. Booleanos: INTEGER 0/1.
-- Las claves foráneas se activan en Conexion.py (PRAGMA foreign_keys = ON).
-- =====================================================================

-- ---------------------------------------------------------------------
-- Clínicas, laboratorio y personas
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clinica (
    id_clinica   INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT NOT NULL UNIQUE,
    direccion    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS laboratorio (
    id_laboratorio  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT NOT NULL UNIQUE,
    direccion       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cliente (
    dni       TEXT PRIMARY KEY,
    nombre    TEXT NOT NULL,
    apellido  TEXT NOT NULL,
    telefono  TEXT NOT NULL,
    email     TEXT,
    activo    INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS veterinario (
    matricula     TEXT PRIMARY KEY,
    dni           TEXT NOT NULL UNIQUE,
    nombre        TEXT NOT NULL,
    apellido      TEXT NOT NULL,
    telefono      TEXT,
    email         TEXT,
    especialidad  TEXT,
    id_clinica    INTEGER NOT NULL REFERENCES clinica(id_clinica),
    turno_laboral TEXT NOT NULL CHECK (turno_laboral IN ('Mañana', 'Tarde'))   -- Mañana 09-13 / Tarde 16-20
);

CREATE TABLE IF NOT EXISTS bioquimico (
    matricula       TEXT PRIMARY KEY,
    dni             TEXT NOT NULL UNIQUE,
    nombre          TEXT NOT NULL,
    apellido        TEXT NOT NULL,
    telefono        TEXT,
    email           TEXT,
    id_laboratorio  INTEGER NOT NULL REFERENCES laboratorio(id_laboratorio)
);

-- ---------------------------------------------------------------------
-- Mascotas, vacunas y agenda
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mascota (
    id_mascota        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre            TEXT NOT NULL,
    especie           TEXT NOT NULL,
    raza              TEXT,
    fecha_nacimiento  TEXT,
    peso              REAL CHECK (peso > 0),
    activa            INTEGER NOT NULL DEFAULT 1,
    dni_responsable   TEXT NOT NULL REFERENCES cliente(dni)   -- Toda mascota debe tener responsable
);

CREATE TABLE IF NOT EXISTS vacuna_aplicada (
    id_vacuna         INTEGER PRIMARY KEY AUTOINCREMENT,
    id_mascota        INTEGER NOT NULL REFERENCES mascota(id_mascota),
    nombre            TEXT NOT NULL,
    fecha_aplicacion  TEXT NOT NULL
);

-- Catálogo de vacunas que se pueden aplicar a cada especie
CREATE TABLE IF NOT EXISTS vacuna_catalogo (
    especie        TEXT NOT NULL,      -- en minúsculas: 'canino', 'felino'
    nombre_vacuna  TEXT NOT NULL,
    obligatoria    INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (especie, nombre_vacuna)
);

CREATE TABLE IF NOT EXISTS turno (
    id_turno               INTEGER PRIMARY KEY AUTOINCREMENT,
    inicio                 TEXT NOT NULL,
    tipo                   TEXT NOT NULL CHECK (tipo IN ('Consulta', 'Control')),
    duracion_minutos       INTEGER NOT NULL CHECK (duracion_minutos BETWEEN 30 AND 90),
    id_mascota             INTEGER NOT NULL REFERENCES mascota(id_mascota),
    matricula_veterinario  TEXT NOT NULL REFERENCES veterinario(matricula),
    motivo                 TEXT,
    cancelado              INTEGER NOT NULL DEFAULT 0
);

-- ---------------------------------------------------------------------
-- Atención clínica
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS consulta (
    id_consulta            INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora             TEXT NOT NULL,
    id_mascota             INTEGER NOT NULL REFERENCES mascota(id_mascota),
    matricula_veterinario  TEXT NOT NULL REFERENCES veterinario(matricula),
    id_clinica             INTEGER NOT NULL REFERENCES clinica(id_clinica),
    tipo_atencion          TEXT NOT NULL CHECK (tipo_atencion IN ('Consulta', 'Control', 'Urgencia')),
    motivo                 TEXT NOT NULL,
    costo                  REAL NOT NULL CHECK (costo >= 0),
    diagnostico            TEXT,
    tratamiento            TEXT,
    id_turno               INTEGER UNIQUE REFERENCES turno(id_turno)   -- NULL si fue una urgencia sin turno
);

-- Vacunas que faltaban al momento de la atención (control de esquema obligatorio)
CREATE TABLE IF NOT EXISTS consulta_vacuna_pendiente (
    id_consulta    INTEGER NOT NULL REFERENCES consulta(id_consulta),
    nombre_vacuna  TEXT NOT NULL,
    PRIMARY KEY (id_consulta, nombre_vacuna)
);

CREATE TABLE IF NOT EXISTS comprobante (
    id_comprobante  INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_emision   TEXT NOT NULL,
    id_consulta     INTEGER NOT NULL REFERENCES consulta(id_consulta)
);

CREATE TABLE IF NOT EXISTS item_comprobante (
    id_item         INTEGER PRIMARY KEY AUTOINCREMENT,
    id_comprobante  INTEGER NOT NULL REFERENCES comprobante(id_comprobante),
    descripcion     TEXT NOT NULL,
    importe         REAL NOT NULL CHECK (importe >= 0)
);

-- ---------------------------------------------------------------------
-- Derivación, logística y laboratorio
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orden_derivacion (
    id_orden        INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_emision   TEXT NOT NULL,
    id_consulta     INTEGER NOT NULL REFERENCES consulta(id_consulta),
    tipo_estudio    TEXT NOT NULL,
    id_laboratorio  INTEGER NOT NULL REFERENCES laboratorio(id_laboratorio)
);

CREATE TABLE IF NOT EXISTS conservadora (
    numero                INTEGER PRIMARY KEY,   -- número físico de la conservadora
    capacidad_maxima      INTEGER NOT NULL CHECK (capacidad_maxima > 0),
    temperatura_objetivo  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS remito (
    id_remito            INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_emision        TEXT NOT NULL,
    id_clinica           INTEGER NOT NULL REFERENCES clinica(id_clinica),
    id_laboratorio       INTEGER NOT NULL REFERENCES laboratorio(id_laboratorio),
    numero_conservadora  INTEGER NOT NULL REFERENCES conservadora(numero),
    estado               TEXT NOT NULL DEFAULT 'En preparación'
                         CHECK (estado IN ('En preparación', 'En tránsito', 'Recibido', 'Rechazado')),
    transportista        TEXT,
    fecha_despacho       TEXT,
    fecha_recepcion      TEXT,
    matricula_receptor   TEXT REFERENCES bioquimico(matricula)
);

CREATE TABLE IF NOT EXISTS precinto (
    codigo         TEXT PRIMARY KEY,
    id_remito      INTEGER NOT NULL UNIQUE REFERENCES remito(id_remito),   -- 1 a 1 con el remito
    inspeccionado  INTEGER NOT NULL DEFAULT 0,
    intacto        INTEGER,                                               -- NULL hasta la inspección
    observaciones  TEXT
);

CREATE TABLE IF NOT EXISTS evento_traslado (
    id_evento    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_remito    INTEGER NOT NULL REFERENCES remito(id_remito),
    fecha_hora   TEXT NOT NULL,
    ubicacion    TEXT NOT NULL,
    descripcion  TEXT NOT NULL,
    temperatura  REAL
);

CREATE TABLE IF NOT EXISTS muestra (
    codigo_muestra    TEXT PRIMARY KEY,
    tipo_muestra      TEXT NOT NULL,
    fecha_extraccion  TEXT NOT NULL,
    id_orden          INTEGER NOT NULL REFERENCES orden_derivacion(id_orden),
    id_remito         INTEGER REFERENCES remito(id_remito),          -- NULL hasta que se empaqueta
    estado            TEXT NOT NULL DEFAULT 'Extraída'
                      CHECK (estado IN ('Extraída', 'Empaquetada', 'En tránsito', 'Recibida', 'Analizada', 'Rechazada')),
    codigo_original   TEXT UNIQUE REFERENCES muestra(codigo_muestra)  -- re-extracción de una muestra rechazada
);

-- Trazabilidad de estados: solo se insertan filas
CREATE TABLE IF NOT EXISTS trazabilidad_muestra (
    id_registro     INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_muestra  TEXT NOT NULL REFERENCES muestra(codigo_muestra),
    estado          TEXT NOT NULL,
    fecha_hora      TEXT NOT NULL,
    motivo          TEXT
);

CREATE TABLE IF NOT EXISTS resultado_analisis (
    id_resultado          INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_muestra        TEXT NOT NULL UNIQUE REFERENCES muestra(codigo_muestra),   -- un resultado por muestra
    fecha_emision         TEXT NOT NULL,
    observaciones         TEXT,
    matricula_bioquimico  TEXT NOT NULL REFERENCES bioquimico(matricula)
);

CREATE TABLE IF NOT EXISTS valor_resultado (
    id_resultado  INTEGER NOT NULL REFERENCES resultado_analisis(id_resultado),
    parametro     TEXT NOT NULL,
    valor         TEXT NOT NULL,
    PRIMARY KEY (id_resultado, parametro)
);

-- ---------------------------------------------------------------------
-- Usuarios del sistema (login simple: contraseña en texto plano)
-- Según el rol, se vincula con el veterinario, bioquímico o cliente que representa.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuario (
    nombre_usuario         TEXT PRIMARY KEY,
    contrasena             TEXT NOT NULL,
    rol                    TEXT NOT NULL CHECK (rol IN ('Secretario', 'Veterinario', 'Bioquímico', 'Cliente')),
    matricula_veterinario  TEXT REFERENCES veterinario(matricula),
    matricula_bioquimico   TEXT REFERENCES bioquimico(matricula),
    dni_cliente            TEXT REFERENCES cliente(dni)
);
