from datetime import datetime, timezone


class EstadoOrden:
    EMITIDA = "emitida"
    EMPAQUETADA = "empaquetada"
    RESULTADO_DISPONIBLE = "resultado_disponible"


class OrdenDerivacion:
    def __init__(
        self,
        id,
        atencion_id,
        tipo_muestra,
        analisis_solicitado,
        fecha_emision=None,
        estado=EstadoOrden.EMITIDA,
    ):
        if not id.strip():
            raise ValueError("id no puede estar vacío")
        if not atencion_id.strip():
            raise ValueError("atencion_id no puede estar vacío")
        if not tipo_muestra.strip():
            raise ValueError("tipo_muestra no puede estar vacío")
        if not analisis_solicitado.strip():
            raise ValueError("analisis_solicitado no puede estar vacío")

        self.id = id
        self.atencion_id = atencion_id
        self.tipo_muestra = tipo_muestra
        self.analisis_solicitado = analisis_solicitado
        self.fecha_emision = (
            fecha_emision if fecha_emision is not None else datetime.now(timezone.utc)
        )
        self.estado = estado

    def marcar_empaquetada(self):
        if self.estado != EstadoOrden.EMITIDA:
            raise ValueError("Solo se pueden empaquetar órdenes emitidas")
        self.estado = EstadoOrden.EMPAQUETADA

    def marcar_resultado_disponible(self):
        if self.estado != EstadoOrden.EMPAQUETADA:
            raise ValueError("La orden debe estar empaquetada antes de recibir resultados")
        self.estado = EstadoOrden.RESULTADO_DISPONIBLE
