from abc import ABC, abstractmethod

# =====================================================================
# PATRÓN DE DISEÑO: STATE (ciclo de vida de la muestra biológica)
#
# Extraída -> Empaquetada -> En tránsito -> Recibida -> Analizada
#                                        \-> Rechazada (precinto roto)
#
# Cada estado sabe qué transiciones admite. Las no permitidas lanzan
# ValueError, sin necesidad de if/elif en MuestraBiologica.
# =====================================================================


class EstadoMuestra(ABC):
    @abstractmethod
    def nombre(self):
        """Nombre descriptivo del estado (solo para mostrar)."""
        pass

    def es_final(self):
        return False

    def empaquetar(self, muestra, conservadora, fecha_hora):
        raise ValueError(f"No se puede empaquetar una muestra en estado: {self.nombre()}")

    def despachar(self, muestra, fecha_hora):
        raise ValueError(f"No se puede despachar una muestra en estado: {self.nombre()}")

    def recibir(self, muestra, precinto_intacto, fecha_hora):
        raise ValueError(f"No se puede recibir una muestra en estado: {self.nombre()}")

    def analizar(self, muestra, resultado):
        raise ValueError(f"No se puede analizar una muestra en estado: {self.nombre()}")

    def __str__(self):
        return self.nombre()


class EstadoExtraida(EstadoMuestra):
    def nombre(self):
        return "Extraída"

    def empaquetar(self, muestra, conservadora, fecha_hora):
        muestra.cambiar_estado(
            EstadoEmpaquetada(), f"Empaquetada en conservadora #{conservadora.numero}", fecha_hora
        )


class EstadoEmpaquetada(EstadoMuestra):
    def nombre(self):
        return "Empaquetada"

    def despachar(self, muestra, fecha_hora):
        muestra.cambiar_estado(EstadoEnTransito(), "Despachada hacia laboratorio central", fecha_hora)


class EstadoEnTransito(EstadoMuestra):
    def nombre(self):
        return "En tránsito"

    def recibir(self, muestra, precinto_intacto, fecha_hora):
        # Validación de negocio clave: verificar precinto sanitario
        if precinto_intacto:
            muestra.cambiar_estado(EstadoRecibida(), "Recibida con precinto sanitario intacto", fecha_hora)
        else:
            # Precinto roto: pasa a Rechazada e impide el análisis
            muestra.cambiar_estado(
                EstadoRechazada(), "Muestra rechazada: precinto sanitario roto o violado", fecha_hora
            )


class EstadoRecibida(EstadoMuestra):
    def nombre(self):
        return "Recibida"

    def analizar(self, muestra, resultado):
        muestra.resultado = resultado
        muestra.cambiar_estado(
            EstadoAnalizada(), "Análisis completado y resultado emitido", resultado.fecha_emision
        )


class EstadoRechazada(EstadoMuestra):
    """Estado terminal: no permite ninguna transición posterior."""

    def nombre(self):
        return "Rechazada"

    def es_final(self):
        return True


class EstadoAnalizada(EstadoMuestra):
    """Estado terminal: ciclo de vida cumplido."""

    def nombre(self):
        return "Analizada"

    def es_final(self):
        return True


# Para reconstruir el estado guardado en la base de datos: "En tránsito" -> EstadoEnTransito
ESTADOS_MUESTRA = {
    clase().nombre(): clase
    for clase in (EstadoExtraida, EstadoEmpaquetada, EstadoEnTransito, EstadoRecibida, EstadoRechazada, EstadoAnalizada)
}
