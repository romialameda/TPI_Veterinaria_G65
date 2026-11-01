from db.fechas import a_texto, a_fecha_hora
from models.Laboratorio.MuestraBiologica import MuestraBiologica, RegistroTrazabilidad
from models.Laboratorio.EstadoMuestra import ESTADOS_MUESTRA


class MuestraDAO:
    """Muestras biológicas y su trazabilidad de estados."""

    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, m):
        self.db.ejecutar(
            """INSERT INTO muestra (codigo_muestra, tipo_muestra, fecha_extraccion, id_orden, estado, codigo_original)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (m.codigo_muestra, m.tipo_muestra, a_texto(m.fecha_extraccion), m.orden_derivacion.numero,
             m.estado_actual.nombre(), m.muestra_original.codigo_muestra if m.muestra_original else None),
        )
        for hito in m.obtener_historial():
            self.insertar_hito(m, hito)

    def actualizar_estado(self, m):
        self.db.ejecutar(
            "UPDATE muestra SET estado = ? WHERE codigo_muestra = ?", (m.estado_actual.nombre(), m.codigo_muestra)
        )

    def actualizar_remito(self, m):
        self.db.ejecutar(
            "UPDATE muestra SET id_remito = ? WHERE codigo_muestra = ?", (m.remito.numero, m.codigo_muestra)
        )

    def insertar_hito(self, m, hito):
        self.db.ejecutar(
            "INSERT INTO trazabilidad_muestra (codigo_muestra, estado, fecha_hora, motivo) VALUES (?, ?, ?, ?)",
            (m.codigo_muestra, hito.estado_nombre, a_texto(hito.fecha_hora), hito.motivo),
        )

    def listar(self, ordenes, remitos):
        """ordenes: {id_orden: OrdenDerivacion}, remitos: {id_remito: RemitoBiologico} ya cargados."""
        historiales = {}
        for f in self.db.consultar("SELECT * FROM trazabilidad_muestra ORDER BY id_registro"):
            estado = ESTADOS_MUESTRA[f["estado"]]()
            historiales.setdefault(f["codigo_muestra"], []).append(
                RegistroTrazabilidad(estado, a_fecha_hora(f["fecha_hora"]), f["motivo"])
            )

        muestras = {}
        originales = {}
        for f in self.db.consultar("SELECT * FROM muestra ORDER BY fecha_extraccion"):
            orden = ordenes[f["id_orden"]]
            m = MuestraBiologica(f["codigo_muestra"], f["tipo_muestra"], a_fecha_hora(f["fecha_extraccion"]), orden)
            m.restaurar(ESTADOS_MUESTRA[f["estado"]](), historiales.get(m.codigo_muestra, []))
            orden.agregar_muestra(m)
            if f["id_remito"] is not None:
                m.remito = remitos[f["id_remito"]]
                m.remito.muestras.append(m)
            if f["codigo_original"]:
                originales[m.codigo_muestra] = f["codigo_original"]
            muestras[m.codigo_muestra] = m

        # Vincula re-extracciones con la muestra rechazada que reemplazan
        for codigo, codigo_original in originales.items():
            muestras[codigo].muestra_original = muestras[codigo_original]
            muestras[codigo_original].reemplazada_por = muestras[codigo]

        return list(muestras.values())
