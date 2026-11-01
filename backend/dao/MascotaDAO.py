from db.fechas import a_texto, a_fecha
from models.clinica.Mascota import Mascota
from models.clinica.Vacuna import Vacuna


class MascotaDAO:
    """Mascotas y sus vacunas aplicadas."""

    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, m):
        cursor = self.db.ejecutar(
            """INSERT INTO mascota (nombre, especie, raza, fecha_nacimiento, peso, activa, dni_responsable)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (m.nombre, m.especie, m.raza, a_texto(m.fecha_nacimiento), m.peso, int(m.activa), m.responsable.dni),
        )
        m.id_mascota = cursor.lastrowid

    def actualizar(self, m):
        self.db.ejecutar(
            "UPDATE mascota SET nombre = ?, raza = ?, peso = ?, activa = ? WHERE id_mascota = ?",
            (m.nombre, m.raza, m.peso, int(m.activa), m.id_mascota),
        )

    def insertar_vacuna(self, mascota, vacuna):
        cursor = self.db.ejecutar(
            "INSERT INTO vacuna_aplicada (id_mascota, nombre, fecha_aplicacion) VALUES (?, ?, ?)",
            (mascota.id_mascota, vacuna.nombre, a_texto(vacuna.fecha_aplicacion)),
        )
        vacuna.id_vacuna = cursor.lastrowid

    def listar(self, clientes):
        """clientes: {dni: Cliente} ya cargados. Devuelve las mascotas con sus vacunas."""
        mascotas = {}
        for f in self.db.consultar("SELECT * FROM mascota ORDER BY id_mascota"):
            responsable = clientes[f["dni_responsable"]]
            m = Mascota(f["id_mascota"], f["nombre"], f["especie"], f["raza"],
                        a_fecha(f["fecha_nacimiento"]), f["peso"], responsable)
            m.activa = bool(f["activa"])
            responsable.agregar_mascota(m)
            mascotas[m.id_mascota] = m

        for f in self.db.consultar("SELECT * FROM vacuna_aplicada ORDER BY fecha_aplicacion"):
            vacuna = Vacuna(f["nombre"], a_fecha(f["fecha_aplicacion"]))
            vacuna.id_vacuna = f["id_vacuna"]
            mascotas[f["id_mascota"]].registrar_vacuna(vacuna)

        return list(mascotas.values())
