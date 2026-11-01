from abc import ABC, abstractmethod

from models.Laboratorio.EstadoMuestra import EstadoAnalizada, EstadoRechazada

# =====================================================================
# PATRÓN DE DISEÑO: OBSERVER
#
# Desacopla MuestraBiologica de las acciones secundarias que se disparan
# ante un cambio de estado (auditoría y notificaciones al cliente).
#
# - SRP: MuestraBiologica no gestiona logs ni envíos.
# - OCP: se pueden sumar observadores sin modificar MuestraBiologica.
# =====================================================================


class ObservadorMuestra(ABC):
    """Interfaz del observador: contrato para quien quiera enterarse de los cambios de estado."""

    @abstractmethod
    def actualizar(self, muestra, nuevo_estado, motivo):
        """Invocado por MuestraBiologica en cada transición de estado."""
        pass


class AuditorTrazabilidad(ObservadorMuestra):
    """Observador concreto: registra cada transición en una bitácora para auditoría."""

    def __init__(self):
        self.bitacora = []

    def actualizar(self, muestra, nuevo_estado, motivo):
        registro = (
            f"[AUDITORÍA] Muestra #{muestra.codigo_muestra} cambió a "
            f"'{nuevo_estado.nombre()}' | Motivo: {motivo}"
        )
        self.bitacora.append(registro)
        print(f"  -> {registro}")


class NotificadorCliente(ObservadorMuestra):
    """
    Observador concreto: avisos al responsable de la mascota.
    - Analizada: un único email cuando TODAS las muestras vigentes de la orden están analizadas.
    - Rechazada: alerta inmediata por WhatsApp para coordinar una nueva extracción.
    """

    def __init__(self):
        self.enviados = []

    def actualizar(self, muestra, nuevo_estado, motivo):
        orden = muestra.orden_derivacion
        responsable = orden.consulta.mascota.responsable
        mascota = orden.consulta.mascota

        if isinstance(nuevo_estado, EstadoAnalizada) and orden.todas_muestras_analizadas():
            mensaje = (
                f"Email a {responsable.email}: todos los resultados del estudio "
                f"'{orden.tipo_estudio}' de {mascota.nombre} están listos."
            )
        elif isinstance(nuevo_estado, EstadoRechazada):
            mensaje = (
                f"WhatsApp a {responsable.telefono}: la muestra {muestra.codigo_muestra} de "
                f"{mascota.nombre} fue rechazada ({motivo}). Coordinar nueva extracción."
            )
        else:
            return

        self.enviados.append(mensaje)
        print(f"  -> [NOTIFICACIÓN] {mensaje}")
