-- Datos que el sistema necesita para funcionar. Se cargan solo si no existen.

-- Catálogo de vacunas por especie (obligatoria = 1 entra en el control de esquema obligatorio)
INSERT OR IGNORE INTO vacuna_catalogo (especie, nombre_vacuna, obligatoria) VALUES
    ('canino', 'Antirrábica', 1),
    ('canino', 'Séxtuple', 1),
    ('canino', 'Tos de las perreras', 0),
    ('canino', 'Giardia', 0),
    ('felino', 'Antirrábica', 1),
    ('felino', 'Triple Felina', 1),
    ('felino', 'Leucemia Felina', 0);
