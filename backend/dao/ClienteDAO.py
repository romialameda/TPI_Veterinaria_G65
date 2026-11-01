from models.clinica.Cliente import Cliente


class ClienteDAO:
    def __init__(self, conexion):
        self.db = conexion

    def insertar(self, cliente):
        self.db.ejecutar(
            "INSERT INTO cliente (dni, nombre, apellido, telefono, email, activo) VALUES (?, ?, ?, ?, ?, ?)",
            (cliente.dni, cliente.nombre, cliente.apellido, cliente.telefono, cliente.email, int(cliente.activo)),
        )

    def actualizar(self, cliente):
        self.db.ejecutar(
            "UPDATE cliente SET nombre = ?, apellido = ?, telefono = ?, email = ?, activo = ? WHERE dni = ?",
            (cliente.nombre, cliente.apellido, cliente.telefono, cliente.email, int(cliente.activo), cliente.dni),
        )

    def listar(self):
        clientes = []
        for f in self.db.consultar("SELECT * FROM cliente ORDER BY apellido, nombre"):
            cliente = Cliente(f["dni"], f["nombre"], f["apellido"], f["telefono"], f["email"])
            cliente.activo = bool(f["activo"])
            clientes.append(cliente)
        return clientes
