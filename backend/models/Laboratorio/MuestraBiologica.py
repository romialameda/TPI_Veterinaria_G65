from datetime import datetime

from models.Laboratorio.EstadoMuestra import (
    EstadoExtraida, EstadoEnTransito, EstadoRecibida, EstadoAnalizada, EstadoRechazada
)


class RegistroTrazabilidad:
    """Hito en la historia de la muestra."""

    def __init__(self, estado, fecha_hora, motivo):
        self.estado = estado
        self.estado_nombre = estado.nombre()
        self.fecha_hora = fecha_hora
        self.motivo = motivo

    def __str__(self):
        return f"[{self.fecha_hora.strftime('%d/%m/%Y %H:%M:%S')}] {self.estado_nombre} - {self.motivo}"


class MuestraBiologica:
    TIPOS_MUESTRA = (
        "Sangre con EDTA", "Suero (sangre sin anticoagulante)", "Orina por cistocentesis", "Orina por micción",
        "Materia fecal", "Biopsia de tejido", "Hisopado", "Raspado de piel",
    )

    def __init__(self, codigo_muestra, tipo_muestra, fecha_extraccion, orden_derivacion):
        if tipo_muestra not in self.TIPOS_MUESTRA:
            raise ValueError(f"Tipo de muestra inválido: {tipo_muestra}.")
        self.codigo_muestra = codigo_muestra
        self.tipo_muestra = tipo_muestra
        self.fecha_extraccion = fecha_extraccion
        self.orden_derivacion = orden_derivacion
        self.resultado = None
        self.remito = None              # Remito en el que viajó
        self.muestra_original = None    # Si es una re-extracción, la muestra rechazada que reemplaza
        self.reemplazada_por = None     # Si fue rechazada y se volvió a extraer
        self._historial_trazabilidad = []
        self._observadores = []         # Patrón Observer

        # Estado inicial obligatorio: Extraída
        self._estado_actual = EstadoExtraida()
        self._registrar_hito("Muestra extraída en clínica", fecha_extraccion)

    def _registrar_hito(self, motivo, fecha_hora):
        self._historial_trazabilidad.append(RegistroTrazabilidad(self._estado_actual, fecha_hora, motivo))

    # --- PATRÓN OBSERVER ---
    def agregar_observador(self, observador):
        if observador not in self._observadores:
            self._observadores.append(observador)

    def notificar_observadores(self, nuevo_estado, motivo):
        for obs in self._observadores:
            obs.actualizar(self, nuevo_estado, motivo)

    # --- TRANSICIÓN DE ESTADO (la invocan los estados) ---
    def cambiar_estado(self, nuevo_estado, motivo="", fecha_hora=None):
        self._estado_actual = nuevo_estado
        self._registrar_hito(motivo, fecha_hora or datetime.now())
        self.notificar_observadores(nuevo_estado, motivo)

    @property
    def estado_actual(self):
        return self._estado_actual

    # --- DELEGACIÓN AL PATRÓN STATE ---
    def empaquetar(self, conservadora, fecha_hora=None):
        self._estado_actual.empaquetar(self, conservadora, fecha_hora)

    def despachar(self, fecha_hora=None):
        self._estado_actual.despachar(self, fecha_hora)

    def recibir(self, precinto_intacto, fecha_hora=None):
        self._estado_actual.recibir(self, precinto_intacto, fecha_hora)

    def analizar(self, resultado):
        self._estado_actual.analizar(self, resultado)

    def restaurar(self, estado, historial):
        """Solo para reconstruir la muestra desde la base de datos (no notifica a los observadores)."""
        self._estado_actual = estado
        self._historial_trazabilidad = list(historial)

    # --- CONSULTAS DE ESTADO ---
    def esta_extraida(self):
        return isinstance(self._estado_actual, EstadoExtraida)

    def esta_analizada(self):
        return isinstance(self._estado_actual, EstadoAnalizada)

    def esta_rechazada(self):
        return isinstance(self._estado_actual, EstadoRechazada)

    def fecha_de_estado(self, clase_estado):
        """Fecha en que la muestra ingresó a un estado (None si nunca pasó por él)."""
        for hito in self._historial_trazabilidad:
            if isinstance(hito.estado, clase_estado):
                return hito.fecha_hora
        return None

    def horas_en_transito(self):
        salida = self.fecha_de_estado(EstadoEnTransito)
        # Llega al laboratorio tanto si se recibe como si se rechaza
        llegada = self.fecha_de_estado(EstadoRecibida) or self.fecha_de_estado(EstadoRechazada)
        if salida is None or llegada is None:
            return None
        return (llegada - salida).total_seconds() / 3600

    def horas_de_procesamiento(self):
        llegada, analisis = self.fecha_de_estado(EstadoRecibida), self.fecha_de_estado(EstadoAnalizada)
        if llegada is None or analisis is None:
            return None
        return (analisis - llegada).total_seconds() / 3600

    def obtener_historial(self):
        """Copia de la trazabilidad de estados (no se puede modificar la lista original)."""
        return list(self._historial_trazabilidad)

    def __str__(self):
        return (
            f"Muestra #{self.codigo_muestra} ({self.tipo_muestra}) | "
            f"Orden #{self.orden_derivacion.numero} | Estado: {self._estado_actual.nombre()}"
        )
