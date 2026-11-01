from models.Laboratorio.Laboratorio import Laboratorio
from models.Laboratorio.Bioquimico import Bioquimico
from models.Laboratorio.MuestraBiologica import MuestraBiologica
from models.Laboratorio.ResultadoAnalisis import ResultadoAnalisis
from models.Laboratorio.ObserverMuestra import AuditorTrazabilidad, NotificadorCliente
from models.Logistica.Conservadora import Conservadora
from models.Logistica.RemitoBiologico import RemitoBiologico
from models.Logistica.EventoTraslado import EventoTraslado
from dao.LaboratorioDAO import LaboratorioDAO
from dao.BioquimicoDAO import BioquimicoDAO
from dao.ConservadoraDAO import ConservadoraDAO
from dao.MuestraDAO import MuestraDAO
from dao.RemitoDAO import RemitoDAO
from dao.ResultadoDAO import ResultadoDAO
from dao.PersistidorMuestra import PersistidorMuestra


class ServicioLaboratorio:
    """
    Casos de uso de los procesos 4 a 7: extracción y empaquetado de muestras, cadena de envío,
    recepción con verificación del precinto y registro de resultados.
    Conecta los observadores (auditoría, notificaciones y persistencia) a cada muestra.
    """

    def __init__(self, repositorio):
        self.repo = repositorio
        self.db = repositorio.conexion
        self.laboratorio_dao = LaboratorioDAO(self.db)
        self.bioquimico_dao = BioquimicoDAO(self.db)
        self.conservadora_dao = ConservadoraDAO(self.db)
        self.muestra_dao = MuestraDAO(self.db)
        self.remito_dao = RemitoDAO(self.db)
        self.resultado_dao = ResultadoDAO(self.db)

        self.auditor = AuditorTrazabilidad()
        self.notificador = NotificadorCliente()
        self.persistidor = PersistidorMuestra(self.db)
        for muestra in self.repo.muestras.values():  # Muestras que ya estaban en la base
            self._suscribir_observadores(muestra)

    # --- DATOS MAESTROS ---
    def alta_laboratorio(self, nombre, direccion):
        laboratorio = Laboratorio(None, nombre, direccion)
        with self.db.transaccion():
            self.laboratorio_dao.insertar(laboratorio)
        self.repo.laboratorios[laboratorio.id_laboratorio] = laboratorio
        return laboratorio

    def alta_bioquimico(self, dni, nombre, apellido, telefono, email, matricula, laboratorio):
        if matricula in self.repo.bioquimicos:
            raise ValueError(f"Ya existe un bioquímico con matrícula {matricula}.")
        bioquimico = Bioquimico(dni, nombre, apellido, telefono, email, matricula, laboratorio)
        with self.db.transaccion():
            self.bioquimico_dao.insertar(bioquimico)
        laboratorio.agregar_bioquimico(bioquimico)
        self.repo.bioquimicos[matricula] = bioquimico
        return bioquimico

    def alta_conservadora(self, numero, capacidad_maxima, temperatura_objetivo):
        if numero in self.repo.conservadoras:
            raise ValueError(f"Ya existe la conservadora #{numero}.")
        conservadora = Conservadora(numero, capacidad_maxima, temperatura_objetivo)
        with self.db.transaccion():
            self.conservadora_dao.insertar(conservadora)
        self.repo.conservadoras[numero] = conservadora
        return conservadora

    def conservadoras_disponibles(self):
        return [c for c in self.repo.conservadoras.values() if c.esta_disponible()]

    # --- MUESTRAS ---
    def _proximo_codigo(self):
        """El sistema numera las muestras: MUE-000001, MUE-000002, ..."""
        return f"MUE-{len(self.repo.muestras) + 1:06d}"

    def registrar_extraccion(self, tipo_muestra, fecha_extraccion, orden, muestra_original=None):
        codigo_muestra = self._proximo_codigo()
        muestra = MuestraBiologica(codigo_muestra, tipo_muestra, fecha_extraccion, orden)
        muestra.muestra_original = muestra_original
        with self.db.transaccion():
            self.muestra_dao.insertar(muestra)
        if muestra_original is not None:
            muestra_original.reemplazada_por = muestra
        orden.agregar_muestra(muestra)
        self._suscribir_observadores(muestra)
        self.repo.muestras[codigo_muestra] = muestra
        return muestra

    def solicitar_reextraccion(self, muestra_rechazada, fecha_extraccion):
        """Reemplaza una muestra rechazada por una nueva extracción de la misma orden."""
        if not muestra_rechazada.esta_rechazada():
            raise ValueError(f"La muestra {muestra_rechazada.codigo_muestra} no está rechazada.")
        if muestra_rechazada.reemplazada_por is not None:
            raise ValueError(f"La muestra {muestra_rechazada.codigo_muestra} ya fue reemplazada.")
        return self.registrar_extraccion(
            muestra_rechazada.tipo_muestra, fecha_extraccion,
            muestra_rechazada.orden_derivacion, muestra_original=muestra_rechazada,
        )

    def _suscribir_observadores(self, muestra):
        muestra.agregar_observador(self.persistidor)
        muestra.agregar_observador(self.auditor)
        muestra.agregar_observador(self.notificador)

    # --- REMITOS Y CADENA DE ENVÍO ---
    def empaquetar(self, fecha_emision, clinica, laboratorio, conservadora, muestras):
        """Proceso 4: arma el remito (con su precinto) y empaqueta las muestras en la conservadora."""
        # Se valida todo antes de tocar nada, para no dejar muestras empaquetadas a medias
        if not conservadora.esta_disponible():
            raise ValueError(
                f"La conservadora #{conservadora.numero} está en uso en el remito #{conservadora.remito_actual.numero}."
            )
        if not muestras:
            raise ValueError("Un remito debe tener al menos una muestra.")
        if len(muestras) > conservadora.capacidad_maxima:
            raise ValueError(f"La conservadora #{conservadora.numero} admite hasta {conservadora.capacidad_maxima} muestras.")
        for m in muestras:
            if not m.esta_extraida():
                raise ValueError(f"La muestra {m.codigo_muestra} no se puede empaquetar (estado: {m.estado_actual}).")

        remito = RemitoBiologico(None, fecha_emision, clinica, laboratorio, conservadora)  # Toma la conservadora
        try:
            for m in muestras:
                remito.verificar_circuito(m)
            with self.db.transaccion():
                self.remito_dao.insertar(remito)  # Asigna número de remito y código de precinto
                for m in muestras:
                    remito.agregar_muestra(m, fecha_emision)
                    self.muestra_dao.actualizar_remito(m)
        except Exception:
            conservadora.liberar()
            raise
        self.repo.remitos[remito.numero] = remito
        return remito

    def despachar(self, remito, fecha_hora, transportista):
        evento = EventoTraslado(fecha_hora, remito.clinica.nombre, f"Retirado por {transportista}")
        with self.db.transaccion():
            remito.despachar(fecha_hora, transportista)
            remito.registrar_evento(evento)
            self.remito_dao.actualizar(remito)
            self.remito_dao.insertar_evento(remito, evento)

    def registrar_evento_traslado(self, remito, fecha_hora, ubicacion, descripcion, temperatura=None):
        """Proceso 5: registra un punto de la cadena de envío."""
        evento = EventoTraslado(fecha_hora, ubicacion, descripcion, temperatura)
        remito.registrar_evento(evento)
        with self.db.transaccion():
            self.remito_dao.insertar_evento(remito, evento)

    def recibir_remito(self, remito, fecha_hora, precinto_intacto, receptor, observaciones=""):
        """Proceso 6: el bioquímico inspecciona el precinto y registra la recepción."""
        if receptor.laboratorio is not remito.laboratorio:
            raise ValueError(f"{receptor.nombre_completo()} no pertenece a {remito.laboratorio.nombre}.")
        with self.db.transaccion():
            remito.recibir_en_laboratorio(fecha_hora, precinto_intacto, receptor, observaciones)
            self.remito_dao.actualizar(remito)
        receptor.registrar_recepcion(remito)

    # --- RESULTADOS ---
    def registrar_resultado(self, fecha_emision, muestra, valores_obtenidos, observaciones, bioquimico):
        """Proceso 7: carga el resultado; solo es posible si la muestra está Recibida."""
        resultado = ResultadoAnalisis(None, fecha_emision, valores_obtenidos, observaciones, bioquimico)
        with self.db.transaccion():
            muestra.analizar(resultado)  # El estado valida si se puede analizar
            self.resultado_dao.insertar(resultado, muestra)
        bioquimico.firmar_resultado(resultado)
        self.repo.resultados.append(resultado)
        return resultado
