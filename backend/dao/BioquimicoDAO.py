from models.Laboratorio.Bioquimico import Bioquimico


class BioquimicoDAO:
    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, bioq):
        self.db.ejecutar(
            """INSERT INTO bioquimico (matricula, dni, nombre, apellido, telefono, email, id_laboratorio)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (bioq.matricula, bioq.dni, bioq.nombre, bioq.apellido, bioq.telefono, bioq.email,
             bioq.laboratorio.id_laboratorio),
        )

    def listar(self, laboratorios):
        """laboratorios: {id_laboratorio: Laboratorio} ya cargados."""
        bioquimicos = []
        for f in self.db.consultar("SELECT * FROM bioquimico ORDER BY apellido"):
            laboratorio = laboratorios[f["id_laboratorio"]]
            bioq = Bioquimico(f["dni"], f["nombre"], f["apellido"], f["telefono"], f["email"],
                              f["matricula"], laboratorio)
            laboratorio.agregar_bioquimico(bioq)
            bioquimicos.append(bioq)
        return bioquimicos
