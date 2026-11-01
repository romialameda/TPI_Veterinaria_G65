from db.fechas import a_texto, a_fecha_hora
from models.Laboratorio.OrdenDerivacion import OrdenDerivacion


class OrdenDerivacionDAO:
    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, o):
        cursor = self.db.ejecutar(
            """INSERT INTO orden_derivacion (fecha_emision, id_consulta, tipo_estudio, id_laboratorio)
               VALUES (?, ?, ?, ?)""",
            (a_texto(o.fecha_emision), o.consulta.numero, o.tipo_estudio, o.laboratorio.id_laboratorio),
        )
        o.numero = cursor.lastrowid

    def listar(self, consultas, laboratorios):
        ordenes = []
        for f in self.db.consultar("SELECT * FROM orden_derivacion ORDER BY id_orden"):
            consulta = consultas[f["id_consulta"]]
            o = OrdenDerivacion(f["id_orden"], a_fecha_hora(f["fecha_emision"]), consulta,
                                f["tipo_estudio"], laboratorios[f["id_laboratorio"]])
            consulta.agregar_orden(o)
            ordenes.append(o)
        return ordenes
