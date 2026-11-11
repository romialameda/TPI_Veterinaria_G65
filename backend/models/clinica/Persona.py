from abc import ABC, abstractmethod

from models import Validaciones


class Persona(ABC):
    def __init__(self, dni, nombre, apellido, telefono, email):
        self.dni = Validaciones.dni(dni)
        self.nombre = Validaciones.solo_letras(nombre, "Nombre")
        self.apellido = Validaciones.solo_letras(apellido, "Apellido")
        self.telefono = Validaciones.telefono(telefono)
        self.email = Validaciones.email(email)

    @abstractmethod
    def rol(self):
        pass

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def __str__(self):
        return f"[{self.rol()}] DNI: {self.dni} - {self.nombre_completo()} - Tel: {self.telefono}"