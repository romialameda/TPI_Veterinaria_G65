class ConsultaMedica:
    def __init__(self, numero, fecha_hora, mascota, veterinario, motivo, costo):
        self.numero = numero
        self.fecha_hora = fecha_hora
        self.mascota = mascota
        self.veterinario = veterinario
        self.motivo = motivo
        self.costo = costo
        self.diagnostico = ""
        self.tratamiento = ""
        self.orden_derivacion = None  # Se completa si requiere laboratorio

        # Agrega la consulta automáticamente al historial de la mascota
        self.mascota.registrar_consulta(self)

    def registrar_diagnostico(self, diagnostico, tratamiento):
        self.diagnostico = diagnostico
        self.tratamiento = tratamiento

    def generar_derivacion(self, orden_derivacion):
        """Asocia la orden de derivación emitida para análisis complejos."""
        self.orden_derivacion = orden_derivacion

    def tiene_derivacion(self):
        return self.orden_derivacion is not None

    def __str__(self):
        derivacion_str = "Con derivación" if self.tiene_derivacion() else "Sin derivación"
        return (
            f"Consulta #{self.numero} - Fecha: {self.fecha_hora} | "
            f"Paciente: {self.mascota.nombre} | Vet: {self.veterinario} | "
            f"Estado: {derivacion_str} | Costo: ${self.costo}"
        )