class ResultadoAnalisis:
    def __init__(self, numero, fecha_emision, valores_obtenidos, observaciones, bioquimico):
        self.numero = numero
        self.fecha_emision = fecha_emision
        self.valores_obtenidos = valores_obtenidos  # {"Parámetro": valor}
        self.observaciones = observaciones
        self.bioquimico = bioquimico

    def __str__(self):
        return (
            f"Resultado #{self.numero} - {self.fecha_emision.strftime('%d/%m/%Y %H:%M')} | "
            f"Firma: {self.bioquimico.nombre_completo()} (MP {self.bioquimico.matricula})"
        )
