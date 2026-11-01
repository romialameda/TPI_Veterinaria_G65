"""
Carga actividad de ejemplo (clientes, vacunas, turnos, consultas, muestras, remitos y resultados)
para poder probar la aplicación sin cargar todo a mano.

La API lo ejecuta una sola vez, cuando crea la base vacía. Las fechas se calculan a partir del
día en que se crea la base, así siempre hay turnos para hoy y mañana y actividad de los días previos.

Todo se carga a través de los servicios (las mismas validaciones que usa la aplicación).
La única excepción son los turnos de hoy y de días anteriores: el sistema no deja agendar en el
pasado, así que esos se agregan directamente a la agenda para simular que se dieron antes.
"""
from datetime import date, datetime, time, timedelta

from dao.TurnoDAO import TurnoDAO
from models.clinica.Turno import Turno


def cargar_datos_demo(repo, clientes, atencion, laboratorio, usuarios):
    hoy = date.today()

    def momento(dias, hora, minuto=0):
        """Fecha y hora relativa a hoy: momento(-2, 10) = anteayer a las 10:00."""
        return datetime.combine(hoy + timedelta(days=dias), time(hora, minuto))

    def turno_ya_dado(inicio, tipo, mascota, vet, motivo):
        """Turno de hoy o de un día anterior, como si se hubiera dado con anticipación."""
        turno = Turno(None, inicio, tipo, mascota, vet, motivo)
        vet.agendar_turno(turno)  # Valida horario y superposición
        with repo.conexion.transaccion():
            TurnoDAO(repo.conexion).insertar(turno)
        repo.turnos.append(turno)
        return turno

    # --- Profesionales, sedes y conservadoras (vienen de datos_ejemplo.sql) ---
    lopez, herrera = repo.veterinarios["5541"], repo.veterinarios["6032"]      # Sede Centro: mañana / tarde
    gomez, acosta = repo.veterinarios["4120"], repo.veterinarios["5877"]       # Sede Norte: mañana / tarde
    tevez = repo.bioquimicos["8812"]
    centro, norte = repo.clinicas[1], repo.clinicas[2]
    lab = repo.laboratorios[1]
    conservadora_12, conservadora_15 = repo.conservadoras[12], repo.conservadoras[15]

    # --- Clientes y mascotas (Laura, Simón y Mora vienen de datos_ejemplo.sql) ---
    simon, mora = repo.mascotas[1], repo.mascotas[2]
    for dni, nombre, apellido, telefono, email in [
        ("40111222", "Martín", "Ruiz", "351-5550000", "martin.ruiz@email.com"),
        ("33222111", "Ana", "Pérez", "351-6661111", "ana.perez@email.com"),
    ]:
        cliente = clientes.alta_cliente(dni, nombre, apellido, telefono, email)
        usuarios.crear_usuario(dni, "1234", "Cliente", cliente)
    rocco = clientes.alta_mascota("Rocco", "Canino", "Mestizo", date(2019, 9, 3), 18.0, "40111222")
    luna = clientes.alta_mascota("Luna", "Felino", "Siamés", date(2023, 4, 20), 3.8, "33222111")
    toby = clientes.alta_mascota("Toby", "Canino", "Beagle", date(2022, 11, 5), 12.5, "33222111")

    # --- Vacunas: algunas al día, una vencida y algunas faltantes ---
    clientes.registrar_vacuna(simon.id_mascota, "Antirrábica", hoy - timedelta(days=200))
    clientes.registrar_vacuna(simon.id_mascota, "Séxtuple", hoy - timedelta(days=200))
    clientes.registrar_vacuna(rocco.id_mascota, "Antirrábica", hoy - timedelta(days=300))
    clientes.registrar_vacuna(luna.id_mascota, "Antirrábica", hoy - timedelta(days=400))   # Vencida
    clientes.registrar_vacuna(toby.id_mascota, "Séxtuple", hoy - timedelta(days=30))

    # =================================================================
    # Hace 3 días: Simón con turno -> panel infeccioso -> resultados listos
    # =================================================================
    t = turno_ya_dado(momento(-3, 9), "Consulta", simon, lopez, "Fiebre y decaimiento")
    c = atencion.atender_turno(t, momento(-3, 9), 18000.0)
    atencion.registrar_diagnostico(c, "Sospecha de infección bacteriana", "Antipirético; se deriva panel infeccioso")
    orden = atencion.emitir_orden_derivacion(momento(-3, 9, 30), c, "Panel infeccioso", lab)
    sangre = laboratorio.registrar_extraccion("Sangre con EDTA", momento(-3, 9, 35), orden)
    orina = laboratorio.registrar_extraccion("Orina por cistocentesis", momento(-3, 9, 40), orden)
    remito = laboratorio.empaquetar(momento(-3, 10), centro, lab, conservadora_12, [sangre, orina])
    laboratorio.despachar(remito, momento(-3, 10, 30), "Logística Andina - Móvil 3")
    laboratorio.registrar_evento_traslado(remito, momento(-3, 11), "Ruta 9 km 15", "Control de temperatura", 4.2)
    laboratorio.recibir_remito(remito, momento(-3, 12), True, tevez)
    laboratorio.registrar_resultado(momento(-3, 15), sangre, {"Leucocitos": "18.500/µL (elevado)", "Hematocrito": "42%"},
                                    "Leucocitosis compatible con infección bacteriana.", tevez)
    laboratorio.registrar_resultado(momento(-3, 17), orina, {"Densidad": "1.025", "Bacterias": "Abundantes"},
                                    "Compatible con cistitis bacteriana.", tevez)
    atencion.emitir_comprobante(momento(-3, 17, 30), c, 4500.0)

    # =================================================================
    # Hace 2 días: Rocco de urgencia -> biopsia -> precinto roto -> re-extracción en tránsito
    # =================================================================
    c = atencion.registrar_urgencia(momento(-2, 10), rocco, gomez, "Decaimiento y pérdida de apetito", 25000.0)
    atencion.registrar_diagnostico(c, "Hepatomegalia a la palpación", "Hepatoprotector; biopsia hepática")
    orden = atencion.emitir_orden_derivacion(momento(-2, 10, 30), c, "Histopatología", lab)
    biopsia = laboratorio.registrar_extraccion("Biopsia de tejido", momento(-2, 10, 45), orden)
    remito = laboratorio.empaquetar(momento(-2, 11), norte, lab, conservadora_15, [biopsia])
    laboratorio.despachar(remito, momento(-2, 11, 30), "Logística Andina - Móvil 7")
    laboratorio.registrar_evento_traslado(remito, momento(-2, 12), "Ruta 19 km 12", "Bache fuerte, conservadora golpeada", 9.0)
    laboratorio.recibir_remito(remito, momento(-2, 13), False, tevez, "Precinto cortado y tapa mal cerrada")
    # Ayer se volvió a extraer y hoy está viajando (el bioquímico tiene que recibirlo)
    biopsia_2 = laboratorio.solicitar_reextraccion(biopsia, momento(-1, 10))
    remito = laboratorio.empaquetar(momento(-1, 10, 30), norte, lab, conservadora_15, [biopsia_2])
    laboratorio.despachar(remito, momento(-1, 11), "Logística Andina - Móvil 7")

    # =================================================================
    # Ayer a la tarde: Luna (control, vacuna vencida) -> urianálisis recibido, falta analizar
    # =================================================================
    t = turno_ya_dado(momento(-1, 16, 30), "Control", luna, herrera, "Control anual")
    c = atencion.atender_turno(t, momento(-1, 16, 30), 12000.0)
    atencion.registrar_diagnostico(c, "Buen estado general", "Se indica refuerzo de vacunas")
    orden = atencion.emitir_orden_derivacion(momento(-1, 17), c, "Urianálisis", lab)
    orina_luna = laboratorio.registrar_extraccion("Orina por micción", momento(-1, 17, 5), orden)
    remito = laboratorio.empaquetar(momento(-1, 17, 30), centro, lab, conservadora_12, [orina_luna])
    laboratorio.despachar(remito, momento(-1, 18), "Logística Andina - Móvil 3")
    laboratorio.recibir_remito(remito, momento(-1, 19), True, tevez)

    # Ayer a la tarde: Toby -> coproparasitológico extraído, falta armar el remito (secretario)
    t = turno_ya_dado(momento(-1, 17), "Consulta", toby, acosta, "Diarrea intermitente")
    c = atencion.atender_turno(t, momento(-1, 17), 15000.0)
    atencion.registrar_diagnostico(c, "Gastroenteritis leve", "Dieta blanda y probióticos")
    orden = atencion.emitir_orden_derivacion(momento(-1, 17, 30), c, "Coproparasitológico", lab)
    laboratorio.registrar_extraccion("Materia fecal", momento(-1, 17, 35), orden)

    # Ayer: un turno al que no vino nadie
    turno_ya_dado(momento(-1, 11), "Control", mora, lopez, "Control de peso")

    # =================================================================
    # Hoy y mañana: turnos pendientes de atender
    # =================================================================
    turno_ya_dado(momento(0, 9), "Consulta", mora, lopez, "Estornudos y ojos llorosos")
    turno_ya_dado(momento(0, 10), "Control", simon, lopez, "Control post tratamiento")
    turno_ya_dado(momento(0, 16), "Consulta", luna, herrera, "Refuerzo de vacunas")
    turno_ya_dado(momento(0, 9, 30), "Control", rocco, gomez, "Control hepático")
    turno_ya_dado(momento(0, 17), "Consulta", toby, acosta, "Control de diarrea")
    atencion.agendar_turno(momento(1, 9), "Control", toby, gomez, "Control general")
    atencion.agendar_turno(momento(1, 16, 30), "Consulta", simon, herrera, "Dermatitis en patas")
