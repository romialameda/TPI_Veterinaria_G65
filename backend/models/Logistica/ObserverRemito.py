from abc import ABC, abstractmethod

from models.Logistica.EstadoRemito import RemitoRecibido, RemitoRechazado
from models.Laboratorio.ObserverMuestra import a_quien_avisar
from models.Notificacion import Notificacion

# =====================================================================
# PATRÓN DE DISEÑO: OBSERVER (sujeto: RemitoBiologico)
#
# Cuando el laboratorio registra la recepción de un remito, la clínica que lo envió
# se entera si hubo problemas, sin que RemitoBiologico sepa quién lo está escuchando.
# =====================================================================


class ObservadorRemito(ABC):
    @abstractmethod
    def actualizar(self, remito, nuevo_estado):
        """Invocado por RemitoBiologico en cada cambio de estado."""
        pass


class AvisoClinica(ObservadorRemito):
    """Observador concreto: avisa a la clínica de origen si el envío llegó con problemas."""

    def __init__(self, enviar=None):
        self.enviar = enviar or (lambda notificacion: print(f"  -> [AVISO] {notificacion}"))

    def actualizar(self, remito, nuevo_estado):
        if isinstance(nuevo_estado, RemitoRechazado):
            mensaje = (f"El remito #{remito.numero} llegó al {remito.laboratorio.nombre} con el precinto roto "
                       f"({remito.precinto.observaciones_inspeccion or 'sin observaciones'}). "
                       f"Se rechazaron todas sus muestras ({remito.cantidad_muestras()}); hay que coordinar nuevas extracciones:\n"
                       + "\n".join(a_quien_avisar(m) for m in remito.muestras))
        elif isinstance(nuevo_estado, RemitoRecibido) and remito.recibido_con_observaciones():
            rechazadas = [m for m in remito.muestras if m.esta_rechazada()]
            mensaje = (f"El remito #{remito.numero} se recibió con observaciones: se rechazaron "
                       f"{len(rechazadas)} de {remito.cantidad_muestras()} muestras; hay que coordinar nuevas extracciones:\n"
                       + "\n".join(f"{a_quien_avisar(m)} - motivo: {m.motivo_rechazo().split(': ', 1)[-1]}" for m in rechazadas))
        else:
            return
        self.enviar(Notificacion(remito.fecha_recepcion, "Clínica", remito.clinica.id_clinica, "Sistema", mensaje))
