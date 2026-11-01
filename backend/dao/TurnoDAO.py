from db.fechas import a_texto, a_fecha_hora
from models.clinica.Turno import Turno


class TurnoDAO:
    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, t):
        cursor = self.db.ejecutar(
            """INSERT INTO turno (inicio, tipo, duracion_minutos, id_mascota, matricula_veterinario, motivo, cancelado)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (a_texto(t.inicio), t.tipo, t.duracion_minutos, t.mascota.id_mascota, t.veterinario.matricula,
             t.motivo, int(t.cancelado)),
        )
        t.numero = cursor.lastrowid

    def actualizar(self, t):
        self.db.ejecutar("UPDATE turno SET cancelado = ? WHERE id_turno = ?", (int(t.cancelado), t.numero))

    def listar(self, mascotas, veterinarios):
        turnos = []
        for f in self.db.consultar("SELECT * FROM turno ORDER BY inicio"):
            vet = veterinarios[f["matricula_veterinario"]]
            t = Turno(f["id_turno"], a_fecha_hora(f["inicio"]), f["tipo"],
                      mascotas[f["id_mascota"]], vet, f["motivo"])
            t.cancelado = bool(f["cancelado"])
            vet.turnos.append(t)  # Ya se validaron al guardarlos
            turnos.append(t)
        return turnos
