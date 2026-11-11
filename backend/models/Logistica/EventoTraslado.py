from models import Validaciones


class EventoTraslado:
    """
    Registro de un punto de la cadena de envío (retiro, paso por un control, demora, incidente...).
    Lo carga el secretario con lo que informa el transportista.
    """

    NOVEDADES = (
        "Sin novedad",
        "Demora en el traslado",
        "Golpe o caída de la conservadora",
        "Conservadora abierta o dañada",
        "Cadena de frío interrumpida",
        "Otro",
    )

    def __init__(self, fecha_hora, ubicacion, novedad="Sin novedad", observacion=""):
        if novedad not in self.NOVEDADES:
            raise ValueError(f"Novedad inválida: {novedad}. Opciones: {', '.join(self.NOVEDADES)}")
        observacion = (observacion or "").strip()
        if novedad == "Otro" and not observacion:
            raise ValueError("Si la novedad es 'Otro', hay que describirla en la observación.")
        self.id_evento = None  # Lo asigna la base de datos
        self.fecha_hora = fecha_hora
        self.ubicacion = Validaciones.texto_obligatorio(ubicacion, "Ubicación")
        self.novedad = novedad
        self.observacion = observacion

    def tiene_novedad(self):
        """True si pasó algo que el laboratorio debería tener en cuenta al recibir."""
        return self.novedad != "Sin novedad"

    def __str__(self):
        obs = f" - {self.observacion}" if self.observacion else ""
        return f"[{self.fecha_hora.strftime('%d/%m/%Y %H:%M')}] {self.ubicacion}: {self.novedad}{obs}"
