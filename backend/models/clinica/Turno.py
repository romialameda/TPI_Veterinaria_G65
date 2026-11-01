from datetime import timedelta


class Turno:
    """
    Turno de la agenda médica de un veterinario. Lo carga el secretario.
    La duración no se elige: depende del tipo de turno.
    """

    DURACIONES = {"Consulta": 45, "Control": 30}  # minutos
    DURACION_MINIMA = 30
    DURACION_MAXIMA = 90

    def __init__(self, numero, inicio, tipo, mascota, veterinario, motivo):
        if tipo not in self.DURACIONES:
            raise ValueError(f"Tipo de turno inválido: {tipo}. Opciones: {', '.join(self.DURACIONES)}")
        duracion = self.DURACIONES[tipo]
        if not self.DURACION_MINIMA <= duracion <= self.DURACION_MAXIMA:
            raise ValueError(f"La duración de un turno debe estar entre {self.DURACION_MINIMA} y {self.DURACION_MAXIMA} minutos.")
        self.numero = numero
        self.inicio = inicio
        self.tipo = tipo
        self.duracion_minutos = duracion
        self.mascota = mascota
        self.veterinario = veterinario
        self.motivo = motivo
        self.cancelado = False
        self.consulta = None  # Se completa cuando el veterinario lo atiende

    @property
    def atendido(self):
        return self.consulta is not None

    @property
    def fin(self):
        return self.inicio + timedelta(minutes=self.duracion_minutos)

    def se_superpone_con(self, otro):
        """Dos turnos se superponen si uno empieza antes de que termine el otro."""
        return self.inicio < otro.fin and otro.inicio < self.fin

    def cancelar(self):
        if self.atendido:
            raise ValueError("No se puede cancelar un turno que ya fue atendido.")
        self.cancelado = True

    def __str__(self):
        estado = " (CANCELADO)" if self.cancelado else ""
        return (
            f"Turno #{self.numero} - {self.inicio.strftime('%d/%m/%Y %H:%M')} a {self.fin.strftime('%H:%M')} | "
            f"{self.tipo}: {self.mascota.nombre} ({self.mascota.especie}) con {self.veterinario.nombre_completo()} | "
            f"{self.motivo}{estado}"
        )
