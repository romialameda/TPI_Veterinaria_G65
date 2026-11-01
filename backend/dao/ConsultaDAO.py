from db.fechas import a_texto, a_fecha_hora
from models.clinica.ConsultaMedica import ConsultaMedica


class ConsultaDAO:
    """Consultas médicas y las vacunas pendientes detectadas en cada una."""

    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, c):
        cursor = self.db.ejecutar(
            """INSERT INTO consulta (fecha_hora, id_mascota, matricula_veterinario, id_clinica, tipo_atencion,
                                     motivo, costo, diagnostico, tratamiento, id_turno)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (a_texto(c.fecha_hora), c.mascota.id_mascota, c.veterinario.matricula, c.clinica.id_clinica,
             c.tipo_atencion, c.motivo, c.costo, c.diagnostico, c.tratamiento,
             c.turno.numero if c.turno else None),
        )
        c.numero = cursor.lastrowid
        for vacuna in c.vacunas_pendientes_detectadas:
            self.db.ejecutar(
                "INSERT INTO consulta_vacuna_pendiente (id_consulta, nombre_vacuna) VALUES (?, ?)",
                (c.numero, vacuna),
            )

    def actualizar_diagnostico(self, c):
        self.db.ejecutar(
            "UPDATE consulta SET diagnostico = ?, tratamiento = ? WHERE id_consulta = ?",
            (c.diagnostico, c.tratamiento, c.numero),
        )

    def listar(self, mascotas, veterinarios, turnos):
        """turnos: {id_turno: Turno} ya cargados."""
        consultas = {}
        for f in self.db.consultar("SELECT * FROM consulta ORDER BY fecha_hora"):
            vet = veterinarios[f["matricula_veterinario"]]
            mascota = mascotas[f["id_mascota"]]
            turno = turnos[f["id_turno"]] if f["id_turno"] else None
            c = ConsultaMedica(f["id_consulta"], a_fecha_hora(f["fecha_hora"]), mascota, vet,
                               f["motivo"], f["costo"], f["tipo_atencion"], turno)
            if turno:
                turno.consulta = c
            c.diagnostico = f["diagnostico"] or ""
            c.tratamiento = f["tratamiento"] or ""
            mascota.registrar_consulta(c)
            vet.registrar_consulta(c)
            c.clinica.registrar_consulta(c)
            consultas[c.numero] = c

        for f in self.db.consultar("SELECT * FROM consulta_vacuna_pendiente"):
            consultas[f["id_consulta"]].vacunas_pendientes_detectadas.append(f["nombre_vacuna"])

        return list(consultas.values())
