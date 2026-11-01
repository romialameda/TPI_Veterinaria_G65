from models.Usuario import Usuario


class UsuarioDAO:
    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, u):
        self.db.ejecutar(
            """INSERT INTO usuario (nombre_usuario, contrasena, rol, matricula_veterinario,
                                    matricula_bioquimico, dni_cliente)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (u.nombre_usuario, u.contrasena, u.rol,
             u.persona.matricula if u.rol == "Veterinario" else None,
             u.persona.matricula if u.rol == "Bioquímico" else None,
             u.persona.dni if u.rol == "Cliente" else None),
        )

    def hay_usuarios(self):
        return self.db.consultar("SELECT COUNT(*) AS n FROM usuario")[0]["n"] > 0

    def listar(self, veterinarios, bioquimicos, clientes):
        usuarios = []
        for f in self.db.consultar("SELECT * FROM usuario"):
            if f["rol"] == "Veterinario":
                persona = veterinarios[f["matricula_veterinario"]]
            elif f["rol"] == "Bioquímico":
                persona = bioquimicos[f["matricula_bioquimico"]]
            elif f["rol"] == "Cliente":
                persona = clientes[f["dni_cliente"]]
            else:
                persona = None
            usuarios.append(Usuario(f["nombre_usuario"], f["contrasena"], f["rol"], persona))
        return usuarios
