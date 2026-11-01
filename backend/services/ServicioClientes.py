from datetime import date

from models.clinica.Cliente import Cliente
from models.clinica.Mascota import Mascota
from models.clinica.Vacuna import Vacuna
from models.clinica.EsquemaVacunacion import EsquemaVacunacion
from dao.ClienteDAO import ClienteDAO
from dao.MascotaDAO import MascotaDAO


class ServicioClientes:
    """Casos de uso de los procesos 1 y 2: administrar clientes, mascotas e historias clínicas."""

    def __init__(self, repositorio):
        self.repo = repositorio
        self.db = repositorio.conexion
        self.cliente_dao = ClienteDAO(self.db)
        self.mascota_dao = MascotaDAO(self.db)

    # --- CLIENTES ---
    def alta_cliente(self, dni, nombre, apellido, telefono, email):
        if dni in self.repo.clientes:
            raise ValueError(f"Ya existe un cliente con DNI {dni}.")
        cliente = Cliente(dni, nombre, apellido, telefono, email)
        with self.db.transaccion():
            self.cliente_dao.insertar(cliente)
        self.repo.clientes[dni] = cliente
        return cliente

    def buscar_cliente(self, dni):
        cliente = self.repo.clientes.get(dni)
        if cliente is None or not cliente.activo:
            raise ValueError(f"No existe un cliente activo con DNI {dni}.")
        return cliente

    def listar_clientes(self):
        return [c for c in self.repo.clientes.values() if c.activo]

    def buscar_clientes_por_apellido(self, texto):
        texto = texto.lower()
        return [c for c in self.listar_clientes() if texto in c.apellido.lower()]

    def modificar_cliente(self, dni, telefono=None, email=None):
        cliente = self.buscar_cliente(dni)
        cliente.actualizar_contacto(telefono, email)
        with self.db.transaccion():
            self.cliente_dao.actualizar(cliente)
        return cliente

    def baja_cliente(self, dni):
        cliente = self.buscar_cliente(dni)
        if cliente.mascotas_activas():
            raise ValueError(
                f"No se puede dar de baja a {cliente.nombre_completo()}: tiene mascotas activas a cargo."
            )
        cliente.dar_de_baja()
        with self.db.transaccion():
            self.cliente_dao.actualizar(cliente)

    # --- MASCOTAS ---
    def alta_mascota(self, nombre, especie, raza, fecha_nacimiento, peso, dni_responsable):
        responsable = self.buscar_cliente(dni_responsable)
        if especie not in EsquemaVacunacion.especies():
            raise ValueError(f"Especie no admitida: {especie}. Opciones: {', '.join(EsquemaVacunacion.especies())}")
        mascota = Mascota(None, nombre, especie, raza, fecha_nacimiento, peso, responsable)
        with self.db.transaccion():
            self.mascota_dao.insertar(mascota)  # Asigna el id autogenerado
        responsable.agregar_mascota(mascota)
        self.repo.mascotas[mascota.id_mascota] = mascota
        return mascota

    def buscar_mascota(self, id_mascota):
        mascota = self.repo.mascotas.get(id_mascota)
        if mascota is None:
            raise ValueError(f"No existe una mascota con id {id_mascota}.")
        return mascota

    def modificar_mascota(self, id_mascota, peso=None, raza=None):
        mascota = self.buscar_mascota(id_mascota)
        if peso is not None:
            mascota.peso = peso
        if raza is not None:
            mascota.raza = raza
        with self.db.transaccion():
            self.mascota_dao.actualizar(mascota)
        return mascota

    def baja_mascota(self, id_mascota):
        mascota = self.buscar_mascota(id_mascota)
        mascota.dar_de_baja()
        with self.db.transaccion():
            self.mascota_dao.actualizar(mascota)

    def registrar_vacuna(self, id_mascota, nombre, fecha_aplicacion):
        mascota = self.buscar_mascota(id_mascota)
        EsquemaVacunacion.validar_vacuna(mascota.especie, nombre)
        if fecha_aplicacion > date.today():
            raise ValueError("La fecha de aplicación no puede ser futura.")
        vacuna = Vacuna(nombre, fecha_aplicacion)
        mascota.registrar_vacuna(vacuna)  # Valida que no esté vigente
        try:
            with self.db.transaccion():
                self.mascota_dao.insertar_vacuna(mascota, vacuna)
        except Exception:
            mascota.vacunas_aplicadas.remove(vacuna)
            raise
        return vacuna

    def historia_clinica(self, id_mascota):
        return self.buscar_mascota(id_mascota).historia_clinica()
