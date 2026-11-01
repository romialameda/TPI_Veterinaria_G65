class EventoTraslado:
    """Registro de un punto de la cadena de envío (salida, paso por un punto de control, llegada)."""

    def __init__(self, fecha_hora, ubicacion, descripcion, temperatura_registrada=None):
        self.id_evento = None  # Lo asigna la base de datos
        self.fecha_hora = fecha_hora
        self.ubicacion = ubicacion
        self.descripcion = descripcion
        self.temperatura_registrada = temperatura_registrada  # °C medidos en la conservadora

    def __str__(self):
        temp = f" | {self.temperatura_registrada}°C" if self.temperatura_registrada is not None else ""
        return f"[{self.fecha_hora.strftime('%d/%m/%Y %H:%M')}] {self.ubicacion}: {self.descripcion}{temp}"
