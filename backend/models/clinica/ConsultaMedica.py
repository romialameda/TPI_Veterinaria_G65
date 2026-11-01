class ConsultaMedica:
    """
    Atención clínica de una mascota. Diagnóstico y tratamiento son texto libre,
    tal como lo escribe el veterinario.
    Puede venir de un turno (Consulta o Control) o ser una urgencia sin turno.
    """

    TIPOS_ATENCION = ("Consulta", "Control", "Urgencia")

    def __init__(self, numero, fecha_hora, mascota, veterinario, motivo, costo, tipo_atencion="Consulta", turno=None):
        if tipo_atencion not in self.TIPOS_ATENCION:
            raise ValueError(f"Tipo de atención inválido: {tipo_atencion}. Opciones: {', '.join(self.TIPOS_ATENCION)}")
        if costo < 0:
            raise ValueError("El costo de la consulta no puede ser negativo.")
        if turno is not None and (turno.mascota is not mascota or turno.veterinario is not veterinario):
            raise ValueError("La consulta debe ser de la mascota y el veterinario del turno.")

        self.numero = numero
        self.fecha_hora = fecha_hora
        self.mascota = mascota
        self.veterinario = veterinario
        self.clinica = veterinario.clinica
        self.tipo_atencion = tipo_atencion
        self.motivo = motivo
        self.costo = costo
        self.turno = turno
        self.diagnostico = ""
        self.tratamiento = ""
        self.ordenes_derivacion = []          # Una consulta puede generar varias órdenes
        self.vacunas_pendientes_detectadas = []  # Resultado del control de vacunas al atender

    def registrar_diagnostico(self, diagnostico, tratamiento):
        self.diagnostico = diagnostico
        self.tratamiento = tratamiento

    def agregar_orden(self, orden_derivacion):
        self.ordenes_derivacion.append(orden_derivacion)

    def tiene_derivacion(self):
        return len(self.ordenes_derivacion) > 0

    def verificar_vacunacion_obligatoria(self):
        """Control del esquema de vacunas obligatorias al registrar la atención."""
        self.vacunas_pendientes_detectadas = self.mascota.vacunas_pendientes(self.fecha_hora.date())
        return list(self.vacunas_pendientes_detectadas)

    def __str__(self):
        derivacion_str = f"{len(self.ordenes_derivacion)} derivación(es)" if self.tiene_derivacion() else "Sin derivación"
        return (
            f"{self.tipo_atencion} #{self.numero} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')} | "
            f"Paciente: {self.mascota.nombre} | Vet: {self.veterinario.nombre_completo()} | "
            f"{self.clinica.nombre} | {derivacion_str} | Costo: ${self.costo:,.2f}"
        )
