-- =====================================================================
-- Datos de ejemplo para usar la aplicación web.
-- La API los carga una sola vez, cuando la base todavía no tiene usuarios.
-- Acá van los datos fijos (sedes, profesionales, usuarios). La actividad (turnos,
-- consultas, muestras...) la genera db/datos_demo.py con fechas relativas al día de hoy.
-- Todas las contraseñas son 1234.
-- =====================================================================

INSERT INTO clinica (id_clinica, nombre, direccion) VALUES
    (1, 'Sede Centro', 'Av. Colón 1200'),
    (2, 'Sede Norte', 'Av. Rafael Núñez 4500');

INSERT INTO laboratorio (id_laboratorio, nombre, direccion) VALUES
    (1, 'Laboratorio Central', 'Bv. San Juan 800');

-- Un veterinario por turno laboral (mañana / tarde) en cada sede
INSERT INTO veterinario (matricula, dni, nombre, apellido, telefono, email, especialidad, id_clinica, turno_laboral) VALUES
    ('5541', '28111222', 'Mariana', 'López', '351-1112222', 'mlopez@vet.com', 'Clínica general', 1, 'Mañana'),
    ('6032', '31444555', 'Sofía', 'Herrera', '351-4445555', 'sherrera@vet.com', 'Dermatología', 1, 'Tarde'),
    ('4120', '30222333', 'Esteban', 'Gómez', '351-2223333', 'egomez@vet.com', 'Cirugía', 2, 'Mañana'),
    ('5877', '29666777', 'Pablo', 'Acosta', '351-6667777', 'pacosta@vet.com', 'Clínica general', 2, 'Tarde');

INSERT INTO bioquimico (matricula, dni, nombre, apellido, telefono, email, id_laboratorio) VALUES
    ('8812', '25333444', 'Carlos', 'Tevez', '351-3334444', 'ctevez@lab.com', 1);

INSERT INTO conservadora (numero, capacidad_maxima, temperatura_objetivo) VALUES
    (12, 10, '4°C'),
    (15, 4, '4°C'),
    (18, 6, '4°C');

INSERT INTO cliente (dni, nombre, apellido, telefono, email) VALUES
    ('35890123', 'Laura', 'Fernández', '351-4567890', 'laura.fernandez@email.com');

INSERT INTO mascota (id_mascota, nombre, especie, raza, fecha_nacimiento, peso, dni_responsable) VALUES
    (1, 'Simón', 'Canino', 'Golden Retriever', '2021-06-15', 31.5, '35890123'),
    (2, 'Mora', 'Felino', 'Europeo', '2022-02-01', 4.2, '35890123');

INSERT INTO usuario (nombre_usuario, contrasena, rol, matricula_veterinario, matricula_bioquimico, dni_cliente) VALUES
    ('secretario', '1234', 'Secretario', NULL, NULL, NULL),
    ('mlopez', '1234', 'Veterinario', '5541', NULL, NULL),
    ('sherrera', '1234', 'Veterinario', '6032', NULL, NULL),
    ('egomez', '1234', 'Veterinario', '4120', NULL, NULL),
    ('pacosta', '1234', 'Veterinario', '5877', NULL, NULL),
    ('ctevez', '1234', 'Bioquímico', NULL, '8812', NULL),
    ('35890123', '1234', 'Cliente', NULL, NULL, '35890123');
