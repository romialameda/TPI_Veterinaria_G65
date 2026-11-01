from datetime import datetime, timedelta

from models.clinica.Persona import Persona
from models.clinica.HorarioAtencion import HorarioAtencion
from models.clinica.Turno import Turno


class Veterinario(Persona):
    """
    Profesional que atiende en una clínica de la red, en el turno mañana o tarde.
    Conoce su agenda (turnos) y las consultas que realizó; a través de ellas,
    las mascotas que atendió. No conoce al resto de las mascotas de la red.
    """

    INTERVALO_AGENDA = 15  # Los turnos empiezan en múltiplos de 15 minutos

    def __init__(self, dni, nombre, apellido, telefono, email, matricula, especialidad, clinica, turno_laboral):
        super().__init__(dni, nombre, apellido, telefono, email)
        HorarioAtencion.validar(turno_laboral)
        self.matricula = matricula
        self.especialidad = especialidad
        self.clinica = clinica
        self.turno_laboral = turno_laboral
        self.turnos = []
        self.consultas = []

    def rol(self):
        return "Veterinario"

    # --- AGENDA ---
    def atiende_en(self, inicio, fin):
        """True si el rango horario está dentro de su turno laboral."""
        return (inicio.date() == fin.date()
                and inicio.time() >= HorarioAtencion.inicio(self.turno_laboral)
                and fin.time() <= HorarioAtencion.fin(self.turno_laboral))

    def agendar_turno(self, turno):
        """Valida el horario de atención y que no haya superposición de turnos."""
        if not self.atiende_en(turno.inicio, turno.fin):
            raise ValueError(
                f"{self.nombre_completo()} atiende en el turno {HorarioAtencion.texto(self.turno_laboral)}: "
                f"el turno de {turno.inicio.strftime('%H:%M')} a {turno.fin.strftime('%H:%M')} queda fuera de su horario."
            )
        for existente in self.turnos_activos():
            if existente.se_superpone_con(turno):
                raise ValueError(
                    f"El turno de las {turno.inicio.strftime('%d/%m/%Y %H:%M')} se superpone con "
                    f"otro turno de {self.nombre_completo()} "
                    f"({existente.inicio.strftime('%H:%M')} a {existente.fin.strftime('%H:%M')})."
                )
        self.turnos.append(turno)

    def turnos_activos(self):
        return [t for t in self.turnos if not t.cancelado]

    def agenda_del_dia(self, dia):
        return sorted(
            [t for t in self.turnos_activos() if t.inicio.date() == dia],
            key=lambda t: t.inicio,
        )

    def horarios_disponibles(self, dia, tipo_turno, desde=None):
        """Horarios de inicio libres para un turno de ese tipo (sin superposición y después de 'desde')."""
        duracion = timedelta(minutes=Turno.DURACIONES[tipo_turno])
        inicio = datetime.combine(dia, HorarioAtencion.inicio(self.turno_laboral))
        cierre = datetime.combine(dia, HorarioAtencion.fin(self.turno_laboral))
        ocupados = self.agenda_del_dia(dia)
        libres = []
        while inicio + duracion <= cierre:
            fin = inicio + duracion
            libre = all(not (inicio < t.fin and t.inicio < fin) for t in ocupados)
            if libre and (desde is None or inicio >= desde):
                libres.append(inicio)
            inicio += timedelta(minutes=self.INTERVALO_AGENDA)
        return libres

    # --- ATENCIONES ---
    def registrar_consulta(self, consulta):
        self.consultas.append(consulta)

    def mascotas_atendidas(self):
        mascotas = []
        for c in self.consultas:
            if c.mascota not in mascotas:
                mascotas.append(c.mascota)
        return mascotas

    def __str__(self):
        return (f"{super().__str__()} | MP {self.matricula} - {self.especialidad} - {self.clinica.nombre} "
                f"- Turno {HorarioAtencion.texto(self.turno_laboral)}")
