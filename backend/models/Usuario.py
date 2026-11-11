class Usuario:
    """
    Usuario del sistema. La contraseña se guarda y compara en texto plano
    (simplificación del TP: no se cifra ni se usan tokens).
    """

    ROLES = ("Secretario", "Veterinario", "Bioquímico", "Cliente")

    def __init__(self, nombre_usuario, contrasena, rol, persona=None):
        if rol not in self.ROLES:
            raise ValueError(f"Rol inválido: {rol}")
        if not contrasena or len(contrasena) < 4:
            raise ValueError("La contraseña debe tener al menos 4 caracteres.")
        if rol != "Secretario" and persona is None:
            raise ValueError(f"Un usuario con rol {rol} debe estar asociado a una persona.")
        self.nombre_usuario = nombre_usuario
        self.contrasena = contrasena
        self.rol = rol
        self.persona = persona  # Veterinario, Bioquimico o Cliente (None para el secretario)

    def contrasena_correcta(self, contrasena):
        return self.contrasena == contrasena
