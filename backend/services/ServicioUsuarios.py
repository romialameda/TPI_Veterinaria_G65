from models.Usuario import Usuario
from dao.UsuarioDAO import UsuarioDAO


class ServicioUsuarios:
    """Login simple: compara usuario y contraseña con los guardados en la base."""

    def __init__(self, repositorio):
        self.repo = repositorio
        self.db = repositorio.conexion
        self.usuario_dao = UsuarioDAO(self.db)

    def login(self, nombre_usuario, contrasena):
        usuario = self.repo.usuarios.get(nombre_usuario)
        if usuario is None or not usuario.contrasena_correcta(contrasena):
            raise ValueError("Usuario o contraseña incorrectos.")
        if usuario.rol == "Cliente" and not usuario.persona.activo:
            raise ValueError("El cliente está dado de baja.")
        return usuario

    def crear_usuario(self, nombre_usuario, contrasena, rol, persona=None):
        if nombre_usuario in self.repo.usuarios:
            raise ValueError(f"Ya existe el usuario {nombre_usuario}.")
        if not contrasena:
            raise ValueError("La contraseña no puede estar vacía.")
        usuario = Usuario(nombre_usuario, contrasena, rol, persona)
        with self.db.transaccion():
            self.usuario_dao.insertar(usuario)
        self.repo.usuarios[nombre_usuario] = usuario
        return usuario
