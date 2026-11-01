from models.clinica.Persona import Persona


class Bioquimico(Persona):
    """
    Profesional del laboratorio central. Conoce los remitos que recibió y los
    resultados que firmó; no conoce clientes ni historias clínicas.
    """

    def __init__(self, dni, nombre, apellido, telefono, email, matricula, laboratorio):
        super().__init__(dni, nombre, apellido, telefono, email)
        self.matricula = matricula
        self.laboratorio = laboratorio
        self.remitos_recibidos = []
        self.resultados_firmados = []

    def rol(self):
        return "Bioquímico"

    def registrar_recepcion(self, remito):
        self.remitos_recibidos.append(remito)

    def firmar_resultado(self, resultado):
        self.resultados_firmados.append(resultado)

    def __str__(self):
        return f"{super().__str__()} | MP {self.matricula} - {self.laboratorio.nombre}"
