class PrecintoSanitario:
    def __init__(self, codigo):
        self.codigo = codigo
        self.esta_intacto = True  # Nace intacto al precintar la conservadora

    def alterado(self):
        """Simula una alteración, rotura o violación durante el transporte."""
        self.esta_intacto = False

    def es_valido(self):
        return self.esta_intacto

    def __str__(self):
        estado_str = "Intacto / Válido" if self.esta_intacto else "Roto / Violado"
        return f"Precinto #{self.codigo} ({estado_str})"