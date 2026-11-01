class Laboratorio:
    """Laboratorio central de diagnóstico que recibe las derivaciones."""

    def __init__(self, id_laboratorio, nombre, direccion):
        self.id_laboratorio = id_laboratorio
        self.nombre = nombre
        self.direccion = direccion
        self.bioquimicos = []

    def agregar_bioquimico(self, bioquimico):
        if bioquimico not in self.bioquimicos:
            self.bioquimicos.append(bioquimico)

    def __str__(self):
        return f"{self.nombre} ({self.direccion})"
