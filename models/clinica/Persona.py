from abc import ABC, abstractmethod


class Persona(ABC):
    def __init__(self, dni, nombre, apellido, telefono, email):
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.email = email

    @abstractmethod
    def rol(self):
        pass

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def __str__(self):
        return f"[{self.rol()}] DNI: {self.dni} - {self.nombre_completo()} - Tel: {self.telefono}"