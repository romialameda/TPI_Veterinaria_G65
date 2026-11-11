from models.Logistica.EstadoRemito import RemitoEnPreparacion
from models.Logistica.PrecintoSanitario import PrecintoSanitario


class RemitoBiologico:
    """
    Documento que acompaña a una conservadora desde una clínica hasta el laboratorio.
    Al crearse, toma la conservadora y genera su precinto sanitario.
    """

    def __init__(self, numero, fecha_emision, clinica, laboratorio, conservadora):
        conservadora.asignar(self)  # Valida que la conservadora no esté en otro remito

        self.numero = numero
        self.fecha_emision = fecha_emision
        self.clinica = clinica
        self.laboratorio = laboratorio
        self.conservadora = conservadora
        self.precinto = PrecintoSanitario(codigo=f"PREC-{numero}" if numero is not None else None)
        self.muestras = []
        self.eventos = []            # Cadena de envío
        self.transportista = None
        self.fecha_despacho = None
        self.fecha_recepcion = None
        self.receptor = None         # Bioquímico que recibió
        self._estado = RemitoEnPreparacion()
        self._observadores = []      # Patrón Observer

    def asignar_numero(self, numero):
        """Lo usa la base de datos al guardar el remito (el número es autogenerado)."""
        self.numero = numero
        self.precinto.codigo = f"PREC-{numero:06d}"

    def verificar_circuito(self, muestra):
        """La muestra debe ir de la misma clínica al mismo laboratorio que el remito."""
        orden = muestra.orden_derivacion
        if orden.clinica is not self.clinica or orden.laboratorio is not self.laboratorio:
            raise ValueError(
                f"La muestra {muestra.codigo_muestra} no corresponde al circuito "
                f"{self.clinica.nombre} -> {self.laboratorio.nombre} de este remito."
            )

    def restaurar_estado(self, estado):
        """Solo para reconstruir el remito desde la base de datos."""
        self._estado = estado
        if estado.es_final():
            self.conservadora.liberar()

    @property
    def estado_actual(self):
        return self._estado

    # --- PATRÓN OBSERVER ---
    def agregar_observador(self, observador):
        if observador not in self._observadores:
            self._observadores.append(observador)

    def cambiar_estado(self, nuevo_estado):
        self._estado = nuevo_estado
        for observador in self._observadores:
            observador.actualizar(self, nuevo_estado)

    # --- DELEGACIÓN AL PATRÓN STATE ---
    def agregar_muestra(self, muestra, fecha_hora=None):
        self._estado.agregar_muestra(self, muestra, fecha_hora)

    def despachar(self, fecha_hora, transportista):
        self._estado.despachar(self, fecha_hora, transportista)

    def registrar_evento(self, evento):
        self._estado.registrar_evento(self, evento)

    def recibir_en_laboratorio(self, fecha_hora, precinto_intacto, receptor, observaciones="", rechazos=None):
        """El receptor inspecciona el precinto (y cada muestra) e informa cómo llegó."""
        self._estado.recibir(self, fecha_hora, precinto_intacto, observaciones, receptor, rechazos or {})

    def recibido_con_observaciones(self):
        """Llegó con el precinto intacto, pero alguna muestra se rechazó al recibir."""
        return self.precinto.es_valido() and any(m.esta_rechazada() for m in self.muestras)

    def novedades_del_traslado(self):
        """Eventos del viaje con alguna novedad (los ve el bioquímico al recibir)."""
        return [e for e in self.eventos if e.tiene_novedad()]

    def cantidad_muestras(self):
        return len(self.muestras)

    def horas_de_viaje(self):
        if self.fecha_despacho is None or self.fecha_recepcion is None:
            return None
        return (self.fecha_recepcion - self.fecha_despacho).total_seconds() / 3600

    def __str__(self):
        return (
            f"Remito #{self.numero} [{self._estado.nombre()}{' con observaciones' if self.recibido_con_observaciones() else ''}] | "
            f"{self.clinica.nombre} -> {self.laboratorio.nombre} | "
            f"Muestras: {self.cantidad_muestras()} | {self.precinto}"
        )
