from db.fechas import a_texto, a_fecha_hora
from models.Laboratorio.ResultadoAnalisis import ResultadoAnalisis


class ResultadoDAO:
    """Resultados de análisis (informe en texto libre)."""

    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, resultado, muestra):
        cursor = self.db.ejecutar(
            """INSERT INTO resultado_analisis (codigo_muestra, fecha_emision, informe, matricula_bioquimico)
               VALUES (?, ?, ?, ?)""",
            (muestra.codigo_muestra, a_texto(resultado.fecha_emision), resultado.informe, resultado.bioquimico.matricula),
        )
        resultado.numero = cursor.lastrowid

    def listar(self, muestras, bioquimicos):
        """Carga los resultados y los asocia a su muestra y al bioquímico que los firmó."""
        resultados = []
        for f in self.db.consultar("SELECT * FROM resultado_analisis ORDER BY id_resultado"):
            bioq = bioquimicos[f["matricula_bioquimico"]]
            r = ResultadoAnalisis(f["id_resultado"], a_fecha_hora(f["fecha_emision"]), f["informe"], bioq)
            muestras[f["codigo_muestra"]].resultado = r
            bioq.firmar_resultado(r)
            resultados.append(r)
        return resultados
