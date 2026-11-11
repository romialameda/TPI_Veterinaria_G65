from abc import ABC, abstractmethod
from datetime import datetime

from models.Laboratorio.EstadoMuestra import EstadoAnalizada, EstadoRechazada, EstadoRecibida
from models.Notificacion import Notificacion

# =====================================================================
# PATRÓN DE DISEÑO: OBSERVER (sujeto: MuestraBiologica)
#
# Desacopla MuestraBiologica de las acciones que se disparan cuando cambia de estado.
# Observadores concretos:
#   - NotificadorCliente (acá): avisa al responsable de la mascota.
#   - AvisoClinicaMuestra (acá): avisa a la recepción de la clínica si el laboratorio rechaza una muestra.
#   - PersistidorMuestra (dao/PersistidorMuestra.py): guarda el estado y la trazabilidad en la base.
#
# - SRP: MuestraBiologica no se ocupa de avisos ni de la base de datos.
# - OCP: se pueden sumar observadores sin modificar MuestraBiologica.
# =====================================================================


class ObservadorMuestra(ABC):
    """Interfaz del observador: contrato para quien quiera enterarse de los cambios de estado."""

    @abstractmethod
    def actualizar(self, muestra, nuevo_estado, motivo):
        """Invocado por MuestraBiologica en cada transición de estado."""
        pass


class NotificadorCliente(ObservadorMuestra):
    """
    Observador concreto: avisa al responsable de la mascota.
    - Analizada: un aviso cuando TODAS las muestras vigentes de la orden están analizadas.
    - Rechazada: aviso inmediato para coordinar una nueva extracción.
    El envío es simulado: el aviso se entrega a la función 'enviar' (que lo guarda para que el
    cliente lo vea en "Mis avisos"). No hace falta integrar un servicio real de email o WhatsApp.
    """

    def __init__(self, enviar=None):
        self.enviar = enviar or (lambda notificacion: print(f"  -> [AVISO] {notificacion}"))

    def actualizar(self, muestra, nuevo_estado, motivo):
        orden = muestra.orden_derivacion
        mascota = orden.consulta.mascota
        responsable = mascota.responsable

        if isinstance(nuevo_estado, EstadoAnalizada) and orden.todas_muestras_analizadas():
            canal = "Email"
            mensaje = f"Los resultados del estudio '{orden.tipo_estudio}' de {mascota.nombre} ya están listos."
        elif isinstance(nuevo_estado, EstadoRechazada):
            canal = "WhatsApp"
            mensaje = (f"La muestra {muestra.codigo_muestra} ({muestra.tipo_muestra}) de {mascota.nombre} fue rechazada "
                       f"({motivo}). Comunicate con la clínica para coordinar una nueva extracción.")
        else:
            return

        fecha = muestra.obtener_historial()[-1].fecha_hora or datetime.now()
        self.enviar(Notificacion(fecha, "Cliente", responsable.dni, canal, mensaje))


def a_quien_avisar(muestra):
    """Datos para que la recepción ubique al responsable: mascota, dueño con teléfono y veterinario."""
    consulta = muestra.orden_derivacion.consulta
    responsable = consulta.mascota.responsable
    return (f"{muestra.codigo_muestra} ({muestra.tipo_muestra}) de {consulta.mascota.nombre} - "
            f"responsable {responsable.nombre_completo()}, tel. {responsable.telefono} - "
            f"veterinario {consulta.veterinario.nombre_completo()}")


class AvisoClinicaMuestra(ObservadorMuestra):
    """
    Observador concreto: avisa a la recepción de la clínica cuando el laboratorio rechaza una muestra
    que ya había recibido (por ejemplo, al analizarla ve que está coagulada).
    Los rechazos en la recepción del remito los avisa AvisoClinica (observador del remito), así no se repiten.
    """

    def __init__(self, enviar=None):
        self.enviar = enviar or (lambda notificacion: print(f"  -> [AVISO] {notificacion}"))

    def actualizar(self, muestra, nuevo_estado, motivo):
        historial = muestra.obtener_historial()
        if not isinstance(nuevo_estado, EstadoRechazada) or not isinstance(historial[-2].estado, EstadoRecibida):
            return
        mensaje = (f"El laboratorio rechazó una muestra que ya había recibido; hay que coordinar una nueva extracción:\n"
                   f"{a_quien_avisar(muestra)} - motivo: {motivo.split(': ', 1)[-1]}")
        clinica = muestra.orden_derivacion.consulta.clinica
        self.enviar(Notificacion(historial[-1].fecha_hora, "Clínica", clinica.id_clinica, "Sistema", mensaje))
