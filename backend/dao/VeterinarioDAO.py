from models.clinica.Veterinario import Veterinario


class VeterinarioDAO:
    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, vet):
        self.db.ejecutar(
            """INSERT INTO veterinario (matricula, dni, nombre, apellido, telefono, email, especialidad,
                                       id_clinica, turno_laboral)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (vet.matricula, vet.dni, vet.nombre, vet.apellido, vet.telefono, vet.email,
             vet.especialidad, vet.clinica.id_clinica, vet.turno_laboral),
        )

    def listar(self, clinicas):
        """clinicas: {id_clinica: Clinica} ya cargadas."""
        veterinarios = []
        for f in self.db.consultar("SELECT * FROM veterinario ORDER BY apellido"):
            clinica = clinicas[f["id_clinica"]]
            vet = Veterinario(f["dni"], f["nombre"], f["apellido"], f["telefono"], f["email"],
                              f["matricula"], f["especialidad"], clinica, f["turno_laboral"])
            clinica.agregar_veterinario(vet)
            veterinarios.append(vet)
        return veterinarios
