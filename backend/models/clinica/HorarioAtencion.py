from datetime import time


class HorarioAtencion:
    """
    Horario de atención de las clínicas, en dos turnos laborales.
    Cada veterinario trabaja en uno de ellos.
    """

    TURNOS_LABORALES = {
        "Mañana": (time(9, 0), time(13, 0)),
        "Tarde": (time(16, 0), time(20, 0)),
    }

    @classmethod
    def validar(cls, turno_laboral):
        if turno_laboral not in cls.TURNOS_LABORALES:
            raise ValueError(f"Turno laboral inválido: {turno_laboral}. Opciones: {', '.join(cls.TURNOS_LABORALES)}")

    @classmethod
    def inicio(cls, turno_laboral):
        return cls.TURNOS_LABORALES[turno_laboral][0]

    @classmethod
    def fin(cls, turno_laboral):
        return cls.TURNOS_LABORALES[turno_laboral][1]

    @classmethod
    def texto(cls, turno_laboral):
        desde, hasta = cls.TURNOS_LABORALES[turno_laboral]
        return f"{turno_laboral} ({desde.strftime('%H:%M')} a {hasta.strftime('%H:%M')})"
