from datetime import date, timedelta

from models.clinica.EsquemaVacunacion import EsquemaVacunacion
from models import Validaciones


class Mascota:
    def __init__(self, id_mascota, nombre, especie, raza, fecha_nacimiento, peso, responsable):
        # Validación obligatoria: toda mascota debe tener responsable
        if responsable is None:
            raise ValueError("Toda mascota debe tener un responsable asociado.")

        self.id_mascota = id_mascota
        self.nombre = Validaciones.texto_obligatorio(nombre, "Nombre de la mascota", 40)
        self.especie = especie
        self.raza = (raza or "").strip()
        self.fecha_nacimiento = Validaciones.fecha_no_futura(fecha_nacimiento, "fecha de nacimiento")
        self.peso = Validaciones.numero_en_rango(peso, "Peso (kg)", 0.1, 150)
        self.responsable = responsable
        self.activa = True
        self.vacunas_aplicadas = []
        self.consultas = []

    def registrar_vacuna(self, vacuna):
        """No se puede aplicar una vacuna que todavía está vigente (sí su refuerzo, pasado un año)."""
        if self.vacuna_vigente(vacuna.nombre, vacuna.fecha_aplicacion):
            vence = self.ultima_aplicacion(vacuna.nombre).fecha_aplicacion + timedelta(days=EsquemaVacunacion.VIGENCIA_DIAS)
            raise ValueError(
                f"{self.nombre} ya tiene la vacuna {vacuna.nombre} vigente hasta el {vence.strftime('%d/%m/%Y')}."
            )
        self.vacunas_aplicadas.append(vacuna)

    def registrar_consulta(self, consulta):
        self.consultas.append(consulta)

    def dar_de_baja(self):
        """Baja lógica: se conserva la historia clínica."""
        self.activa = False

    def ultima_aplicacion(self, nombre_vacuna, a_fecha=None):
        """Última aplicación de esa vacuna hasta la fecha indicada (None si nunca se aplicó)."""
        a_fecha = a_fecha or date.today()
        aplicadas = [v for v in self.vacunas_aplicadas
                     if v.nombre.lower() == nombre_vacuna.lower() and v.fecha_aplicacion <= a_fecha]
        return max(aplicadas, key=lambda v: v.fecha_aplicacion, default=None)

    def vacuna_vigente(self, nombre_vacuna, a_fecha=None):
        """True si se aplicó hace menos de un año (respecto de a_fecha, por defecto hoy)."""
        a_fecha = a_fecha or date.today()
        ultima = self.ultima_aplicacion(nombre_vacuna, a_fecha)
        return ultima is not None and (a_fecha - ultima.fecha_aplicacion).days < EsquemaVacunacion.VIGENCIA_DIAS

    def vacunas_pendientes(self, a_fecha=None):
        """Vacunas obligatorias de su especie que nunca se aplicaron o que ya vencieron."""
        return [v for v in EsquemaVacunacion.obligatorias_para(self.especie) if not self.vacuna_vigente(v, a_fecha)]

    def historia_clinica(self):
        """Consultas de la mascota ordenadas de la más reciente a la más antigua."""
        return sorted(self.consultas, key=lambda c: c.fecha_hora, reverse=True)

    def __str__(self):
        return (
            f"Mascota #{self.id_mascota}: {self.nombre} ({self.especie} - {self.raza}) "
            f"- Responsable: {self.responsable.nombre_completo()} - Peso: {self.peso}kg"
        )
