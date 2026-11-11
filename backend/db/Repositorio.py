from models.clinica.EsquemaVacunacion import EsquemaVacunacion
from dao.ClinicaDAO import ClinicaDAO
from dao.LaboratorioDAO import LaboratorioDAO
from dao.ClienteDAO import ClienteDAO
from dao.VeterinarioDAO import VeterinarioDAO
from dao.BioquimicoDAO import BioquimicoDAO
from dao.MascotaDAO import MascotaDAO
from dao.VacunaCatalogoDAO import VacunaCatalogoDAO
from dao.TurnoDAO import TurnoDAO
from dao.ConsultaDAO import ConsultaDAO
from dao.OrdenDerivacionDAO import OrdenDerivacionDAO
from dao.ComprobanteDAO import ComprobanteDAO
from dao.ConservadoraDAO import ConservadoraDAO
from dao.RemitoDAO import RemitoDAO
from dao.MuestraDAO import MuestraDAO
from dao.ResultadoDAO import ResultadoDAO
from dao.UsuarioDAO import UsuarioDAO
from dao.NotificacionDAO import NotificacionDAO


class Repositorio:
    """
    Mantiene en memoria UNA sola instancia de cada objeto leído de la base de datos,
    con todas sus relaciones armadas (la mascota apunta a su cliente, la muestra a su remito, etc.).
    Los servicios trabajan sobre estos objetos y guardan cada cambio con los DAOs.
    """

    def __init__(self, conexion):
        self.conexion = conexion
        self.clinicas = {}        # id_clinica -> Clinica
        self.laboratorios = {}    # id_laboratorio -> Laboratorio
        self.clientes = {}        # dni -> Cliente
        self.veterinarios = {}    # matricula -> Veterinario
        self.bioquimicos = {}     # matricula -> Bioquimico
        self.mascotas = {}        # id_mascota -> Mascota
        self.turnos = []
        self.consultas = {}       # id_consulta -> ConsultaMedica
        self.ordenes = {}         # id_orden -> OrdenDerivacion
        self.comprobantes = []
        self.conservadoras = {}   # numero -> Conservadora
        self.remitos = {}         # id_remito -> RemitoBiologico
        self.muestras = {}        # codigo -> MuestraBiologica
        self.resultados = []
        self.usuarios = {}        # nombre_usuario -> Usuario
        self.notificaciones = []

    def cargar(self):
        """Lee toda la base respetando el orden de las claves foráneas."""
        db = self.conexion
        EsquemaVacunacion.cargar(VacunaCatalogoDAO(db).listar_por_especie())

        self.clinicas = {c.id_clinica: c for c in ClinicaDAO(db).listar()}
        self.laboratorios = {l.id_laboratorio: l for l in LaboratorioDAO(db).listar()}
        self.clientes = {c.dni: c for c in ClienteDAO(db).listar()}
        self.veterinarios = {v.matricula: v for v in VeterinarioDAO(db).listar(self.clinicas)}
        self.bioquimicos = {b.matricula: b for b in BioquimicoDAO(db).listar(self.laboratorios)}
        self.mascotas = {m.id_mascota: m for m in MascotaDAO(db).listar(self.clientes)}
        self.turnos = TurnoDAO(db).listar(self.mascotas, self.veterinarios)
        self.consultas = {c.numero: c for c in ConsultaDAO(db).listar(
            self.mascotas, self.veterinarios, {t.numero: t for t in self.turnos})}
        self.ordenes = {o.numero: o for o in OrdenDerivacionDAO(db).listar(self.consultas, self.laboratorios)}
        self.comprobantes = ComprobanteDAO(db).listar(self.consultas)
        self.conservadoras = {c.numero: c for c in ConservadoraDAO(db).listar()}
        self.remitos = {r.numero: r for r in RemitoDAO(db).listar(
            self.clinicas, self.laboratorios, self.conservadoras, self.bioquimicos)}
        self.muestras = {m.codigo_muestra: m for m in MuestraDAO(db).listar(self.ordenes, self.remitos)}
        self.resultados = ResultadoDAO(db).listar(self.muestras, self.bioquimicos)
        self.usuarios = {u.nombre_usuario: u for u in UsuarioDAO(db).listar(
            self.veterinarios, self.bioquimicos, self.clientes)}
        self.notificaciones = NotificacionDAO(db).listar()
        return self
