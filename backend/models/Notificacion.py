class Notificacion:
    """
    Aviso generado por un observador. El envío es simulado: no se manda un mail ni un WhatsApp real,
    sino que el aviso queda guardado y el destinatario lo ve en el sistema ("Mis avisos" / "Avisos").
    """

    DESTINATARIOS = ("Cliente", "Clínica")

    def __init__(self, fecha_hora, destinatario_tipo, destinatario_id, canal, mensaje):
        if destinatario_tipo not in self.DESTINATARIOS:
            raise ValueError(f"Destinatario inválido: {destinatario_tipo}")
        self.id_notificacion = None  # Lo asigna la base de datos
        self.fecha_hora = fecha_hora
        self.destinatario_tipo = destinatario_tipo
        self.destinatario_id = str(destinatario_id)  # DNI del cliente o id de la clínica
        self.canal = canal                           # "Email", "WhatsApp" o "Sistema"
        self.mensaje = mensaje

    def __str__(self):
        return f"[{self.canal} a {self.destinatario_tipo} {self.destinatario_id}] {self.mensaje}"
