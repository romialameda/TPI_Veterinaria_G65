from db.fechas import a_texto, a_fecha_hora
from models.clinica.ComprobanteAtencion import ComprobanteAtencion


class ComprobanteDAO:
    """Comprobantes de atención y sus ítems."""

    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, comp):
        cursor = self.db.ejecutar(
            "INSERT INTO comprobante (fecha_emision, id_consulta) VALUES (?, ?)",
            (a_texto(comp.fecha_emision), comp.consulta.numero),
        )
        comp.numero = cursor.lastrowid
        for item in comp.items:
            cursor = self.db.ejecutar(
                "INSERT INTO item_comprobante (id_comprobante, descripcion, importe) VALUES (?, ?, ?)",
                (comp.numero, item.descripcion, item.importe),
            )
            item.id_item = cursor.lastrowid

    def listar(self, consultas):
        comprobantes = {}
        for f in self.db.consultar("SELECT * FROM comprobante ORDER BY id_comprobante"):
            comp = ComprobanteAtencion(f["id_comprobante"], a_fecha_hora(f["fecha_emision"]),
                                       consultas[f["id_consulta"]])
            comprobantes[comp.numero] = comp

        for f in self.db.consultar("SELECT * FROM item_comprobante ORDER BY id_item"):
            comprobantes[f["id_comprobante"]].agregar_item(f["descripcion"], f["importe"])

        return list(comprobantes.values())
