from models.clinica.Clinica import Clinica


class ClinicaDAO:
    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, clinica):
        cursor = self.db.ejecutar(
            "INSERT INTO clinica (nombre, direccion) VALUES (?, ?)",
            (clinica.nombre, clinica.direccion),
        )
        clinica.id_clinica = cursor.lastrowid

    def listar(self):
        return [
            Clinica(f["id_clinica"], f["nombre"], f["direccion"])
            for f in self.db.consultar("SELECT * FROM clinica ORDER BY id_clinica")
        ]
