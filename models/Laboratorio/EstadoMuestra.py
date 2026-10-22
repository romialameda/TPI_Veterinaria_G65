from abc import ABC, abstractmethod
from datetime import datetime


class EstadoMuestra(ABC):
    @abstractmethod
    def nombre(self):
        """Retorna el nombre descriptivo del estado"""
        pass

    def empaquetar(self, muestra, conservadora):
        raise ValueError(f"No se puede empaquetar una muestra en estado: {self.nombre()}")

    def despachar(self, muestra):
        raise ValueError(f"No se puede despachar una muestra en estado: {self.nombre()}")

    def recibir(self, muestra, precinto_intacto):
        raise ValueError(f"No se puede recibir una muestra en estado: {self.nombre()}")

    def analizar(self, muestra, resultado):
        raise ValueError(f"No se puede analizar una muestra en estado: {self.nombre()}")

    def __str__(self):
        return self.nombre()


class EstadoExtraida(EstadoMuestra):
    def nombre(self):
        return "Extraída"

    def empaquetar(self, muestra, conservadora):
        # Transición válida: pasa a Empaquetada
        muestra.cambiar_estado(EstadoEmpaquetada(), f"Empaquetada en conservadora #{conservadora.numero}")


class EstadoEmpaquetada(EstadoMuestra):
    def nombre(self):
        return "Empaquetada"

    def despachar(self, muestra):
        # Transición válida: inicia el viaje
        muestra.cambiar_estado(EstadoEnTransito(), "Despachada hacia laboratorio central")


class EstadoEnTransito(EstadoMuestra):
    def nombre(self):
        return "En tránsito"

    def recibir(self, muestra, precinto_intacto):
        # Validación de negocio clave: verificar precinto sanitario
        if precinto_intacto:
            muestra.cambiar_estado(EstadoRecibida(), "Recibida con precinto sanitario intacto")
        else:
            # Precinto roto: pasa automáticamente a Rechazada e impide análisis
            muestra.cambiar_estado(EstadoRechazada(), "Muestra Rechazada: precinto sanitario roto o violado")


class EstadoRecibida(EstadoMuestra):
    def nombre(self):
        return "Recibida"

    def analizar(self, muestra, resultado):
        muestra.resultado = resultado
        muestra.cambiar_estado(EstadoAnalizada(), "Análisis completado y resultado emitido")


class EstadoRechazada(EstadoMuestra):
    def nombre(self):
        return "Rechazada"
    # No permite ninguna transición posterior; es un estado terminal


class EstadoAnalizada(EstadoMuestra):
    def nombre(self):
        return "Analizada"
    # Estado final de ciclo de vida cumplido