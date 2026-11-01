from models.Laboratorio.Laboratorio import Laboratorio


class LaboratorioDAO:
    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, laboratorio):
        cursor = self.db.ejecutar(
            "INSERT INTO laboratorio (nombre, direccion) VALUES (?, ?)",
            (laboratorio.nombre, laboratorio.direccion),
        )
        laboratorio.id_laboratorio = cursor.lastrowid

    def listar(self):
        return [
            Laboratorio(f["id_laboratorio"], f["nombre"], f["direccion"])
            for f in self.db.consultar("SELECT * FROM laboratorio ORDER BY id_laboratorio")
        ]
