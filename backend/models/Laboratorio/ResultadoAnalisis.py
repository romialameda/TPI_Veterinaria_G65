from models import Validaciones


class ResultadoAnalisis:
    """Resultado de un análisis: el bioquímico lo escribe como texto libre (informe)."""

    def __init__(self, numero, fecha_emision, informe, bioquimico):
        self.numero = numero
        self.fecha_emision = fecha_emision
        self.informe = Validaciones.texto_obligatorio(informe, "Resultado", 3000)
        self.bioquimico = bioquimico

    def __str__(self):
        return (
            f"Resultado #{self.numero} - {self.fecha_emision.strftime('%d/%m/%Y %H:%M')} | "
            f"Firma: {self.bioquimico.nombre_completo()} (MP {self.bioquimico.matricula})"
        )
