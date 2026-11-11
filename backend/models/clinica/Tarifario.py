class Tarifario:
    """
    Precios fijos de la red. El costo de cada atención sale de su tipo
    (el veterinario no lo carga a mano) y se informa al dar el turno.
    """

    PRECIOS_ATENCION = {
        "Control": 12000.0,    # Turno de 30 minutos
        "Consulta": 18000.0,   # Turno de 45 minutos
        "Urgencia": 30000.0,   # Sin turno: tiene recargo
    }
    ARANCEL_ANALISIS_POR_MUESTRA = 4500.0  # Lo que se le cobra al cliente por cada muestra analizada

    @classmethod
    def precio_atencion(cls, tipo_atencion):
        if tipo_atencion not in cls.PRECIOS_ATENCION:
            raise ValueError(f"No hay precio para el tipo de atención {tipo_atencion}.")
        return cls.PRECIOS_ATENCION[tipo_atencion]
