class Clinica:
    """Sede de la red de clínicas veterinarias."""

    def __init__(self, id_clinica, nombre, direccion):
        self.id_clinica = id_clinica
        self.nombre = nombre
        self.direccion = direccion
        self.veterinarios = []
        self.consultas = []

    def agregar_veterinario(self, veterinario):
        if veterinario not in self.veterinarios:
            self.veterinarios.append(veterinario)

    def registrar_consulta(self, consulta):
        self.consultas.append(consulta)

    def __str__(self):
        return f"{self.nombre} ({self.direccion})"
