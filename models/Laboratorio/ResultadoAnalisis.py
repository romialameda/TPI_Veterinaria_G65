class ResultadoAnalisis:
    def __init__(self, numero, fecha_emision, valores_obtenidos, observaciones, profesional):
        self.numero = numero
        self.fecha_emision = fecha_emision
        self.valores_obtenidos = valores_obtenidos  
        self.observaciones = observaciones
        self.profesional = profesional

    def __str__(self):
        return f"Resultado #{self.numero} - Fecha: {self.fecha_emision} | Firma: {self.profesional}"
