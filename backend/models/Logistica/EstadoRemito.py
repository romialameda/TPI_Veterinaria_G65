from abc import ABC, abstractmethod

from models.Laboratorio.MuestraBiologica import MuestraBiologica

# =====================================================================
# PATRÓN DE DISEÑO: STATE (ciclo de vida del remito biológico)
#
# En preparación -> En tránsito -> Recibido
#                               \-> Rechazado (precinto roto)
#
# El remito coordina a sus muestras: cada transición del remito dispara
# la transición correspondiente de todas sus muestras.
# =====================================================================


class EstadoRemito(ABC):
    @abstractmethod
    def nombre(self):
        pass

    def es_final(self):
        return False

    def agregar_muestra(self, remito, muestra, fecha_hora):
        raise ValueError(f"No se pueden agregar muestras a un remito en estado: {self.nombre()}")

    def despachar(self, remito, fecha_hora, transportista):
        raise ValueError(f"No se puede despachar un remito en estado: {self.nombre()}")

    def registrar_evento(self, remito, evento):
        raise ValueError(f"No se pueden registrar eventos de traslado en estado: {self.nombre()}")

    def recibir(self, remito, fecha_hora, precinto_intacto, observaciones, receptor, rechazos):
        raise ValueError(f"No se puede recibir un remito en estado: {self.nombre()}")

    def __str__(self):
        return self.nombre()


class RemitoEnPreparacion(EstadoRemito):
    def nombre(self):
        return "En preparación"

    def agregar_muestra(self, remito, muestra, fecha_hora):
        if len(remito.muestras) >= remito.conservadora.capacidad_maxima:
            raise ValueError(f"La conservadora #{remito.conservadora.numero} superó su capacidad máxima.")
        remito.verificar_circuito(muestra)
        muestra.empaquetar(remito.conservadora, fecha_hora)  # Extraída -> Empaquetada
        muestra.remito = remito
        remito.muestras.append(muestra)

    def despachar(self, remito, fecha_hora, transportista):
        if not remito.muestras:
            raise ValueError("No se puede despachar un remito sin muestras.")
        if not (transportista or "").strip():
            raise ValueError("Hay que indicar el transportista que retira el remito.")
        remito.fecha_despacho = fecha_hora
        remito.transportista = transportista
        for muestra in remito.muestras:
            muestra.despachar(fecha_hora)  # Empaquetada -> En tránsito
        remito.cambiar_estado(RemitoEnTransito())


class RemitoEnTransito(EstadoRemito):
    def nombre(self):
        return "En tránsito"

    def registrar_evento(self, remito, evento):
        if remito.eventos and evento.fecha_hora < remito.eventos[-1].fecha_hora:
            raise ValueError("Los eventos de traslado deben registrarse en orden cronológico.")
        remito.eventos.append(evento)

    def recibir(self, remito, fecha_hora, precinto_intacto, observaciones, receptor, rechazos):
        """
        rechazos: {codigo_muestra: (motivo, observacion)} para rechazar muestras puntuales
        cuando el precinto llegó intacto. Si el precinto está roto se rechaza todo el contenedor.
        """
        codigos = {m.codigo_muestra for m in remito.muestras}
        for codigo, (motivo, observacion) in rechazos.items():  # Se valida todo antes de cambiar estados
            if codigo not in codigos:
                raise ValueError(f"La muestra {codigo} no viaja en el remito #{remito.numero}.")
            if motivo not in MuestraBiologica.MOTIVOS_RECHAZO:
                raise ValueError(f"Motivo de rechazo inválido: {motivo}.")
            if motivo == "Otro" and not (observacion or "").strip():
                raise ValueError(f"Describí el motivo del rechazo de la muestra {codigo}.")
        remito.precinto.registrar_inspeccion(precinto_intacto, observaciones)
        remito.fecha_recepcion = fecha_hora
        remito.receptor = receptor
        for muestra in remito.muestras:
            if precinto_intacto and muestra.codigo_muestra in rechazos:
                motivo, observacion = rechazos[muestra.codigo_muestra]
                muestra.rechazar(motivo, observacion, fecha_hora)  # Rechazo puntual
            else:
                muestra.recibir(precinto_intacto, fecha_hora)  # -> Recibida o Rechazada (precinto roto)
        remito.conservadora.liberar()
        remito.cambiar_estado(RemitoRecibido() if precinto_intacto else RemitoRechazado())


class RemitoRecibido(EstadoRemito):
    def nombre(self):
        return "Recibido"

    def es_final(self):
        return True


class RemitoRechazado(EstadoRemito):
    def nombre(self):
        return "Rechazado"

    def es_final(self):
        return True


# Para reconstruir el estado guardado en la base de datos
ESTADOS_REMITO = {
    clase().nombre(): clase
    for clase in (RemitoEnPreparacion, RemitoEnTransito, RemitoRecibido, RemitoRechazado)
}
