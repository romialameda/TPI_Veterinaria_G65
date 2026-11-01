from db.fechas import a_texto, a_fecha_hora
from models.Laboratorio.ResultadoAnalisis import ResultadoAnalisis


class ResultadoDAO:
    """Resultados de análisis y sus valores (una fila por parámetro)."""

    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, resultado, muestra):
        cursor = self.db.ejecutar(
            """INSERT INTO resultado_analisis (codigo_muestra, fecha_emision, observaciones, matricula_bioquimico)
               VALUES (?, ?, ?, ?)""",
            (muestra.codigo_muestra, a_texto(resultado.fecha_emision), resultado.observaciones,
             resultado.bioquimico.matricula),
        )
        resultado.numero = cursor.lastrowid
        for parametro, valor in resultado.valores_obtenidos.items():
            self.db.ejecutar(
                "INSERT INTO valor_resultado (id_resultado, parametro, valor) VALUES (?, ?, ?)",
                (resultado.numero, parametro, str(valor)),
            )

    def listar(self, muestras, bioquimicos):
        """Carga los resultados y los asocia a su muestra y al bioquímico que los firmó."""
        valores = {}
        for f in self.db.consultar("SELECT * FROM valor_resultado"):
            valores.setdefault(f["id_resultado"], {})[f["parametro"]] = f["valor"]

        resultados = []
        for f in self.db.consultar("SELECT * FROM resultado_analisis ORDER BY id_resultado"):
            bioq = bioquimicos[f["matricula_bioquimico"]]
            r = ResultadoAnalisis(f["id_resultado"], a_fecha_hora(f["fecha_emision"]),
                                  valores.get(f["id_resultado"], {}), f["observaciones"], bioq)
            muestras[f["codigo_muestra"]].resultado = r
            bioq.firmar_resultado(r)
            resultados.append(r)
        return resultados
