class Conservadora:
    """Contenedor isotérmico reutilizable. Solo puede estar asignado a un remito a la vez."""

    def __init__(self, numero, capacidad_maxima, temperatura_objetivo):
        self.numero = numero
        self.capacidad_maxima = capacidad_maxima
        self.temperatura_objetivo = temperatura_objetivo
        self.remito_actual = None

    def esta_disponible(self):
        return self.remito_actual is None

    def asignar(self, remito):
        if not self.esta_disponible():
            raise ValueError(
                f"La conservadora #{self.numero} está en uso en el remito #{self.remito_actual.numero}."
            )
        self.remito_actual = remito

    def liberar(self):
        self.remito_actual = None

    def __str__(self):
        estado = "Disponible" if self.esta_disponible() else f"En uso (remito #{self.remito_actual.numero})"
        return (
            f"Conservadora #{self.numero} (Capacidad: {self.capacidad_maxima} muestras, "
            f"Temp: {self.temperatura_objetivo}) - {estado}"
        )
