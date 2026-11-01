class EsquemaVacunacion:
    """
    Catálogo de vacunas por especie, indicando cuáles son obligatorias.
    Se carga desde la base de datos (tabla vacuna_catalogo). Se consulta al registrar
    vacunas (solo se aceptan las del catálogo) y al registrar cada atención
    (validación: controlar esquema de vacunas obligatorias).
    """

    VIGENCIA_DIAS = 365  # Las vacunas se refuerzan una vez por año

    # {especie: {nombre_vacuna: es_obligatoria}}. Estos valores se reemplazan por los de la base.
    CATALOGO = {
        "canino": {"Antirrábica": True, "Séxtuple": True},
        "felino": {"Antirrábica": True, "Triple Felina": True},
    }

    @classmethod
    def cargar(cls, catalogo):
        cls.CATALOGO = {especie.lower(): dict(vacunas) for especie, vacunas in catalogo.items()}

    @classmethod
    def _vacunas_de(cls, especie):
        return cls.CATALOGO.get(especie.strip().lower(), {})

    @classmethod
    def especies(cls):
        return [e.capitalize() for e in cls.CATALOGO]

    @classmethod
    def disponibles_para(cls, especie):
        return list(cls._vacunas_de(especie))

    @classmethod
    def obligatorias_para(cls, especie):
        return [nombre for nombre, obligatoria in cls._vacunas_de(especie).items() if obligatoria]

    @classmethod
    def validar_vacuna(cls, especie, nombre):
        if nombre not in cls._vacunas_de(especie):
            raise ValueError(f"La vacuna '{nombre}' no está en el catálogo para la especie {especie}.")
