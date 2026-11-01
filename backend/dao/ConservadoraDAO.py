from models.Logistica.Conservadora import Conservadora


class ConservadoraDAO:
    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, c):
        self.db.ejecutar(
            "INSERT INTO conservadora (numero, capacidad_maxima, temperatura_objetivo) VALUES (?, ?, ?)",
            (c.numero, c.capacidad_maxima, c.temperatura_objetivo),
        )

    def listar(self):
        return [
            Conservadora(f["numero"], f["capacidad_maxima"], f["temperatura_objetivo"])
            for f in self.db.consultar("SELECT * FROM conservadora ORDER BY numero")
        ]
