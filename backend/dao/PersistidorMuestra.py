from models.Laboratorio.ObserverMuestra import ObservadorMuestra
from dao.MuestraDAO import MuestraDAO


class PersistidorMuestra(ObservadorMuestra):
    """
    Observador concreto (patrón Observer): cada vez que una muestra cambia de estado,
    guarda el nuevo estado y el hito de trazabilidad en la base de datos.
    MuestraBiologica no sabe que existe una base de datos.
    """

    def __init__(self, conexion):
        self.dao = MuestraDAO(conexion)

    def actualizar(self, muestra, nuevo_estado, motivo):
        self.dao.actualizar_estado(muestra)
        self.dao.insertar_hito(muestra, muestra.obtener_historial()[-1])
