from db.fechas import a_texto, a_fecha_hora
from models.Logistica.RemitoBiologico import RemitoBiologico
from models.Logistica.EventoTraslado import EventoTraslado
from models.Logistica.EstadoRemito import ESTADOS_REMITO


class RemitoDAO:
    """Remitos biológicos, con su precinto (1 a 1) y sus eventos de traslado."""

    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, r):
        cursor = self.db.ejecutar(
            """INSERT INTO remito (fecha_emision, id_clinica, id_laboratorio, numero_conservadora, estado)
               VALUES (?, ?, ?, ?, ?)""",
            (a_texto(r.fecha_emision), r.clinica.id_clinica, r.laboratorio.id_laboratorio,
             r.conservadora.numero, r.estado_actual.nombre()),
        )
        r.asignar_numero(cursor.lastrowid)  # También genera el código del precinto
        self.db.ejecutar(
            "INSERT INTO precinto (codigo, id_remito) VALUES (?, ?)", (r.precinto.codigo, r.numero)
        )

    def actualizar(self, r):
        """Guarda estado, despacho, recepción e inspección del precinto."""
        self.db.ejecutar(
            """UPDATE remito SET estado = ?, transportista = ?, fecha_despacho = ?, fecha_recepcion = ?,
                                 matricula_receptor = ?
               WHERE id_remito = ?""",
            (r.estado_actual.nombre(), r.transportista, a_texto(r.fecha_despacho), a_texto(r.fecha_recepcion),
             r.receptor.matricula if r.receptor else None, r.numero),
        )
        p = r.precinto
        self.db.ejecutar(
            "UPDATE precinto SET inspeccionado = ?, intacto = ?, observaciones = ? WHERE codigo = ?",
            (int(p.inspeccionado), None if p.esta_intacto is None else int(p.esta_intacto),
             p.observaciones_inspeccion, p.codigo),
        )

    def insertar_evento(self, remito, evento):
        cursor = self.db.ejecutar(
            """INSERT INTO evento_traslado (id_remito, fecha_hora, ubicacion, descripcion, temperatura)
               VALUES (?, ?, ?, ?, ?)""",
            (remito.numero, a_texto(evento.fecha_hora), evento.ubicacion, evento.descripcion,
             evento.temperatura_registrada),
        )
        evento.id_evento = cursor.lastrowid

    def listar(self, clinicas, laboratorios, conservadoras, bioquimicos):
        remitos = {}
        for f in self.db.consultar("SELECT * FROM remito ORDER BY id_remito"):
            r = RemitoBiologico(f["id_remito"], a_fecha_hora(f["fecha_emision"]), clinicas[f["id_clinica"]],
                                laboratorios[f["id_laboratorio"]], conservadoras[f["numero_conservadora"]])
            r.transportista = f["transportista"]
            r.fecha_despacho = a_fecha_hora(f["fecha_despacho"])
            r.fecha_recepcion = a_fecha_hora(f["fecha_recepcion"])
            if f["matricula_receptor"]:
                r.receptor = bioquimicos[f["matricula_receptor"]]
                r.receptor.registrar_recepcion(r)
            r.restaurar_estado(ESTADOS_REMITO[f["estado"]]())  # Libera la conservadora si ya terminó
            remitos[r.numero] = r

        for f in self.db.consultar("SELECT * FROM precinto"):
            p = remitos[f["id_remito"]].precinto
            p.codigo = f["codigo"]
            p.inspeccionado = bool(f["inspeccionado"])
            p.esta_intacto = None if f["intacto"] is None else bool(f["intacto"])
            p.observaciones_inspeccion = f["observaciones"] or ""

        for f in self.db.consultar("SELECT * FROM evento_traslado ORDER BY fecha_hora"):
            evento = EventoTraslado(a_fecha_hora(f["fecha_hora"]), f["ubicacion"], f["descripcion"], f["temperatura"])
            evento.id_evento = f["id_evento"]
            remitos[f["id_remito"]].eventos.append(evento)

        return list(remitos.values())
