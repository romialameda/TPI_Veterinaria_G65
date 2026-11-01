from datetime import datetime

from models.clinica.Clinica import Clinica
from models.clinica.Veterinario import Veterinario
from models.clinica.Turno import Turno
from models.clinica.ConsultaMedica import ConsultaMedica
from models.clinica.ComprobanteAtencion import ComprobanteAtencion
from models.Laboratorio.OrdenDerivacion import OrdenDerivacion
from dao.ClinicaDAO import ClinicaDAO
from dao.VeterinarioDAO import VeterinarioDAO
from dao.TurnoDAO import TurnoDAO
from dao.ConsultaDAO import ConsultaDAO
from dao.OrdenDerivacionDAO import OrdenDerivacionDAO
from dao.ComprobanteDAO import ComprobanteDAO


class ServicioAtencion:
    """
    Casos de uso del proceso 3 y del comprobante del proceso 7: clínicas, veterinarios,
    agenda de turnos, consultas médicas, órdenes de derivación y comprobantes.
    """

    def __init__(self, repositorio):
        self.repo = repositorio
        self.db = repositorio.conexion
        self.clinica_dao = ClinicaDAO(self.db)
        self.veterinario_dao = VeterinarioDAO(self.db)
        self.turno_dao = TurnoDAO(self.db)
        self.consulta_dao = ConsultaDAO(self.db)
        self.orden_dao = OrdenDerivacionDAO(self.db)
        self.comprobante_dao = ComprobanteDAO(self.db)

    # --- CLÍNICAS Y VETERINARIOS ---
    def alta_clinica(self, nombre, direccion):
        clinica = Clinica(None, nombre, direccion)
        with self.db.transaccion():
            self.clinica_dao.insertar(clinica)
        self.repo.clinicas[clinica.id_clinica] = clinica
        return clinica

    def alta_veterinario(self, dni, nombre, apellido, telefono, email, matricula, especialidad, clinica, turno_laboral):
        if matricula in self.repo.veterinarios:
            raise ValueError(f"Ya existe un veterinario con matrícula {matricula}.")
        veterinario = Veterinario(dni, nombre, apellido, telefono, email, matricula, especialidad, clinica, turno_laboral)
        with self.db.transaccion():
            self.veterinario_dao.insertar(veterinario)
        clinica.agregar_veterinario(veterinario)
        self.repo.veterinarios[matricula] = veterinario
        return veterinario

    def buscar_veterinario(self, matricula):
        vet = self.repo.veterinarios.get(matricula)
        if vet is None:
            raise ValueError(f"No existe un veterinario con matrícula {matricula}.")
        return vet

    # --- AGENDA ---
    def agendar_turno(self, inicio, tipo, mascota, veterinario, motivo):
        if not mascota.activa:
            raise ValueError(f"{mascota.nombre} está dada de baja.")
        if inicio < datetime.now():
            raise ValueError("No se puede agendar un turno en una fecha u hora que ya pasó.")
        turno = Turno(None, inicio, tipo, mascota, veterinario, motivo)
        veterinario.agendar_turno(turno)  # Valida horario de atención y superposición
        try:
            with self.db.transaccion():
                self.turno_dao.insertar(turno)
        except Exception:
            veterinario.turnos.remove(turno)
            raise
        self.repo.turnos.append(turno)
        return turno

    def horarios_disponibles(self, veterinario, dia, tipo):
        """Horarios libres del veterinario para ese día y tipo de turno (sin los que ya pasaron)."""
        if tipo not in Turno.DURACIONES:
            raise ValueError(f"Tipo de turno inválido: {tipo}.")
        return veterinario.horarios_disponibles(dia, tipo, desde=datetime.now())

    def cancelar_turno(self, turno):
        turno.cancelar()
        with self.db.transaccion():
            self.turno_dao.actualizar(turno)

    # --- CONSULTAS ---
    def atender_turno(self, turno, fecha_hora, costo):
        """El veterinario atiende un turno: la mascota, el tipo y el motivo salen del turno."""
        if turno.cancelado:
            raise ValueError("El turno está cancelado.")
        if turno.atendido:
            raise ValueError("El turno ya fue atendido.")
        if fecha_hora.date() != turno.inicio.date():
            raise ValueError("Un turno solo se puede atender el día del turno.")
        consulta = self._registrar_consulta(fecha_hora, turno.mascota, turno.veterinario, turno.motivo,
                                            costo, turno.tipo, turno)
        turno.consulta = consulta
        return consulta

    def registrar_urgencia(self, fecha_hora, mascota, veterinario, motivo, costo):
        """Atención sin turno previo."""
        return self._registrar_consulta(fecha_hora, mascota, veterinario, motivo, costo, "Urgencia")

    def _registrar_consulta(self, fecha_hora, mascota, veterinario, motivo, costo, tipo_atencion, turno=None):
        """
        Registra la atención y controla el esquema de vacunas obligatorias.
        Si faltan vacunas no se bloquea la atención: queda registrado para avisar y para el reporte.
        """
        if not mascota.activa:
            raise ValueError(f"{mascota.nombre} está dada de baja.")
        consulta = ConsultaMedica(None, fecha_hora, mascota, veterinario, motivo, costo, tipo_atencion, turno)
        consulta.verificar_vacunacion_obligatoria()
        with self.db.transaccion():
            self.consulta_dao.insertar(consulta)

        mascota.registrar_consulta(consulta)
        veterinario.registrar_consulta(consulta)
        consulta.clinica.registrar_consulta(consulta)
        self.repo.consultas[consulta.numero] = consulta
        return consulta

    def registrar_diagnostico(self, consulta, diagnostico, tratamiento):
        consulta.registrar_diagnostico(diagnostico, tratamiento)
        with self.db.transaccion():
            self.consulta_dao.actualizar_diagnostico(consulta)

    def emitir_orden_derivacion(self, fecha_emision, consulta, tipo_estudio, laboratorio):
        orden = OrdenDerivacion(None, fecha_emision, consulta, tipo_estudio, laboratorio)
        with self.db.transaccion():
            self.orden_dao.insertar(orden)
        consulta.agregar_orden(orden)
        self.repo.ordenes[orden.numero] = orden
        return orden

    # --- COMPROBANTES ---
    def emitir_comprobante(self, fecha_emision, consulta, arancel_por_muestra=0.0):
        """Comprobante de la atención; incluye los análisis ya realizados de sus derivaciones."""
        comprobante = ComprobanteAtencion(None, fecha_emision, consulta)
        comprobante.agregar_item(f"{consulta.tipo_atencion}: {consulta.motivo}"[:45], consulta.costo)
        for orden in consulta.ordenes_derivacion:
            analizadas = [m for m in orden.muestras if m.esta_analizada()]
            if analizadas and arancel_por_muestra > 0:
                comprobante.agregar_item(
                    f"Lab. {orden.tipo_estudio} x{len(analizadas)}"[:45],
                    len(analizadas) * arancel_por_muestra,
                )
        with self.db.transaccion():
            self.comprobante_dao.insertar(comprobante)
        self.repo.comprobantes.append(comprobante)
        return comprobante
