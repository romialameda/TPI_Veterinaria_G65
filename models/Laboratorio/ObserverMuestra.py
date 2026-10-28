from abc import ABC, abstractmethod

# =====================================================================
# PATRÓN DE DISEÑO: OBSERVER (Observador)[cite: 2]
#
# Propósito:
# Desacoplar la entidad MuestraBiologica de las acciones secundarias que
# se disparan ante un cambio de estado (auditoría inmutable y notificaciones)[cite: 1, 2].
#
# Principios aplicados:
# - Single Responsibility Principle (SRP): MuestraBiologica no gestiona logs ni envíos.
# - Open/Closed Principle (OCP): Se pueden sumar nuevos observadores sin modificar la clase muestra.
# =====================================================================

class ObservadorMuestra(ABC):
    """
    Rol: Interfaz del Observador (Subscriber).
    Define el contrato obligatorio que deben implementar todos los componentes
    interesados en los eventos y transiciones del ciclo de vida de la muestra[cite: 2].
    """

    @abstractmethod
    def actualizar(self, muestra, nuevo_estado, motivo):
        """
        Método 'update' invocado por el sujeto observable (MuestraBiologica)
        cada vez que ocurre una transición de estado[cite: 2].
        
        :param muestra: Referencia a la instancia de MuestraBiologica que cambió.
        :param nuevo_estado: Instancia del nuevo EstadoMuestra asignado[cite: 2].
        :param motivo: Descripción textual o justificación del cambio de estado[cite: 2].
        """
        pass


class AuditorTrazabilidad(ObservadorMuestra):
    """
    Rol: Observador Concreto 1.
    Resuelve el requerimiento de negocio de 'Mantener la trazabilidad inmutable
    de estados de la muestra'[cite: 2].
    Almacena secuencialmente cada hito en una bitácora para reportes y auditorías forenses[cite: 2].
    """

    def __init__(self):
        # Bitácora histórica donde se apilan los registros de forma secuencial[cite: 2]
        self.bitacora = []

    def actualizar(self, muestra, nuevo_estado, motivo):
        # Se genera la entrada con los datos del evento[cite: 2]
        registro = (
            f"[AUDITORÍA] Muestra #{muestra.codigo_muestra} cambió a "
            f"'{nuevo_estado.nombre()}' | Motivo: {motivo}"
        )
        self.bitacora.append(registro)
        print(f"  -> {registro}")


class NotificadorCliente(ObservadorMuestra):
    """
    Rol: Observador Concreto 2.
    Resuelve el requerimiento de negocio de 'Enviar recordatorios de controles,
    vacunas o resultados listos' y alertar ante fallas en la cadena de custodia[cite: 1, 2].
    
    Regla de negocio:
    - En caso de éxito (Analizada): solo emite una única notificación al dueño cuando 
      todas las muestras del estudio/orden han sido analizadas[cite: 1, 2].
    - En caso de fallo (Rechazada): emite una alerta inmediata para coordinar una nueva extracción[cite: 2].
    """

    def actualizar(self, muestra, nuevo_estado, motivo):
        nombre_estado = nuevo_estado.nombre()
        orden = muestra.orden_derivacion
        dueño = orden.consulta.mascota.responsable

        # Caso de éxito: verifica que la orden completa esté terminada antes de notificar[cite: 1, 2]
        if nombre_estado == "Analizada":
            if hasattr(orden, "todas_muestras_analizadas") and orden.todas_muestras_analizadas():
                print(
                    f"  -> [NOTIFICACIÓN] Enviando email a {dueño.email}: "
                    f"Todos los resultados del estudio '{orden.tipo_estudio}' de "
                    f"{orden.consulta.mascota.nombre} están listos."
                )

        # Caso de falla: alerta de forma individual e inmediata[cite: 2]
        elif nombre_estado == "Rechazada":
            print(
                f"  -> [ALERTA URGENTE] WhatsApp a {dueño.telefono}: "
                f"La muestra {muestra.codigo_muestra} fue rechazada ({motivo}). Coordinar nueva extracción."
            )