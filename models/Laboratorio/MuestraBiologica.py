from datetime import datetime
from EstadoMuestra import EstadoExtraida


class RegistroTrazabilidad:
    """Representa un hito inmutable en la historia de la muestra."""
    def __init__(self, estado_nombre, fecha_hora, motivo):
        self.estado_nombre = estado_nombre
        self.fecha_hora = fecha_hora
        self.motivo = motivo

    def __str__(self):
        return f"[{self.fecha_hora.strftime('%d/%m/%Y %H:%M:%S')}] {self.estado_nombre} - {self.motivo}"


class MuestraBiologica:
    def __init__(self, codigo_muestra, tipo_muestra, fecha_extraccion, orden_derivacion):
        self.codigo_muestra = codigo_muestra
        self.tipo_muestra = tipo_muestra  
        self.fecha_extraccion = fecha_extraccion
        self.orden_derivacion = orden_derivacion
        self.resultado = None
        self._historial_trazabilidad = []

        # Estado inicial obligatorio: Extraída
        self._estado_actual = EstadoExtraida()
        self._registrar_hito("Muestra extraída en clínica")

    def _registrar_hito(self, motivo):
        hito = RegistroTrazabilidad(self._estado_actual.nombre(), datetime.now(), motivo)
        self._historial_trazabilidad.append(hito)

    def cambiar_estado(self, nuevo_estado, motivo=""):
        self._estado_actual = nuevo_estado
        self._registrar_hito(motivo)

    @property
    def estado_actual(self):
        return self._estado_actual

    # Delegación de operaciones al Patrón State
    def empaquetar(self, conservadora):
        self._estado_actual.empaquetar(self, conservadora)

    def despachar(self):
        self._estado_actual.despachar(self)

    def recibir(self, precinto_intacto):
        self._estado_actual.recibir(self, precinto_intacto)

    def analizar(self, resultado):
        self._estado_actual.analizar(self, resultado)

    def obtener_historial(self):
        """Retorna la copia de la trazabilidad inmutable de estados"""
        return list(self._historial_trazabilidad)

    def __str__(self):
        return (
            f"Muestra #{self.codigo_muestra} ({self.tipo_muestra}) | "
            f"Orden #{self.orden_derivacion.numero} | "
            f"Estado: {self._estado_actual.nombre()}"
        )