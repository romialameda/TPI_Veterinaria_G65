class PrecintoSanitario:
    """
    Precinto que se coloca al cerrar la conservadora. Su estado real se conoce
    recién cuando el laboratorio lo inspecciona en la recepción.
    """

    def __init__(self, codigo):
        self.codigo = codigo
        self.inspeccionado = False
        self.esta_intacto = None
        self.observaciones_inspeccion = ""

    def registrar_inspeccion(self, intacto, observaciones=""):
        if self.inspeccionado:
            raise ValueError(f"El precinto #{self.codigo} ya fue inspeccionado.")
        self.inspeccionado = True
        self.esta_intacto = intacto
        self.observaciones_inspeccion = observaciones

    def es_valido(self):
        return self.inspeccionado and self.esta_intacto

    def __str__(self):
        if not self.inspeccionado:
            estado_str = "Colocado / Sin inspeccionar"
        elif self.esta_intacto:
            estado_str = "Intacto"
        else:
            estado_str = f"Roto / Violado ({self.observaciones_inspeccion})"
        return f"Precinto #{self.codigo} ({estado_str})"
