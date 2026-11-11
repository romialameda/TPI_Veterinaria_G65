from db.fechas import a_texto, a_fecha_hora
from models.Notificacion import Notificacion


class NotificacionDAO:
    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, n):
        cursor = self.db.ejecutar(
            """INSERT INTO notificacion (fecha_hora, destinatario_tipo, destinatario_id, canal, mensaje)
               VALUES (?, ?, ?, ?, ?)""",
            (a_texto(n.fecha_hora), n.destinatario_tipo, n.destinatario_id, n.canal, n.mensaje),
        )
        n.id_notificacion = cursor.lastrowid

    def listar(self):
        notificaciones = []
        for f in self.db.consultar("SELECT * FROM notificacion ORDER BY fecha_hora"):
            n = Notificacion(a_fecha_hora(f["fecha_hora"]), f["destinatario_tipo"], f["destinatario_id"],
                             f["canal"], f["mensaje"])
            n.id_notificacion = f["id_notificacion"]
            notificaciones.append(n)
        return notificaciones
