from Models.Clinica.Persona import Persona
class Cliente(Persona):
    def __init__(self, dni, nombre, apellido, telefono, email):
        super().__init__(dni, nombre, apellido, telefono, email)
        self.mascotas = []

    def rol(self):
        return "Cliente"

    def agregar_mascota(self, mascota):
        if mascota not in self.mascotas:
            self.mascotas.append(mascota)

    def __str__(self):
        return f"{super().__str__()} | Mascotas a cargo: {self.cantidad_mascotas()}"
