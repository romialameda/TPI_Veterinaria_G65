class OrdenDerivacion:
    def __init__(self, numero, fecha_emision, consulta, tipo_estudio, clinica):
        self.numero = numero
        self.fecha_emision = fecha_emision
        self.consulta = consulta
        self.tipo_estudio = tipo_estudio 
        self.clinica = clinica
        self.muestras = []

        # Vinculación con la consulta médica de la clínica
        self.consulta.generar_derivacion(self)

    def agregar_muestra(self, muestra):
        self.muestras.append(muestra)

    def cantidad_muestras(self):
        return len(self.muestras)

    def todas_muestras_analizadas(self):
        """Retorna True si la orden tiene muestras y todas están en estado Analizada."""
        if not self.muestras:
            return False
        return all(m.estado_actual.nombre() == "Analizada" for m in self.muestras)

    def __str__(self):
        return (
            f"Orden #{self.numero} - Estudio: {self.tipo_estudio} | "
            f"Clínica: {self.clinica} | Paciente: {self.consulta.mascota.nombre} | "
            f"Muestras: {self.cantidad_muestras()}"
        )