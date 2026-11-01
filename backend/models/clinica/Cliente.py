from models.clinica.Persona import Persona


class Cliente(Persona):
    """Responsable de una o más mascotas. Solo conoce a sus propias mascotas."""

    def __init__(self, dni, nombre, apellido, telefono, email):
        super().__init__(dni, nombre, apellido, telefono, email)
        self.mascotas = []
        self.activo = True

    def rol(self):
        return "Cliente"

    def agregar_mascota(self, mascota):
        if mascota not in self.mascotas:
            self.mascotas.append(mascota)

    def dar_de_baja(self):
        """Baja lógica: se conserva para no perder la historia clínica de sus mascotas."""
        self.activo = False

    def mascotas_activas(self):
        return [m for m in self.mascotas if m.activa]

    def cantidad_mascotas(self):
        return len(self.mascotas_activas())

    def actualizar_contacto(self, telefono=None, email=None):
        if telefono is not None:
            self.telefono = telefono
        if email is not None:
            self.email = email

    def __str__(self):
        return f"{super().__str__()} | Mascotas a cargo: {self.cantidad_mascotas()}"
