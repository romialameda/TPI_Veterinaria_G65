from datetime import datetime, date, time, timedelta
from pathlib import Path

from db.Conexion import Conexion
from db.Repositorio import Repositorio
from services.ServicioClientes import ServicioClientes
from services.ServicioAtencion import ServicioAtencion
from services.ServicioLaboratorio import ServicioLaboratorio
from Reports.GeneradorReportes import GeneradorReportes
from models.clinica.Tarifario import Tarifario

RUTA_DB_DEMO = Path(__file__).parent / "demo_veterinaria.db"


def titulo(texto):
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


def seccion(texto):
    print(f"\n--- {texto} ---")


def intentar(descripcion, accion):
    """Ejecuta una acción que DEBE fallar por una validación de negocio."""
    try:
        accion()
        print(f"[ERROR] {descripcion}: el sistema no lo impidió")
    except ValueError as e:
        print(f"[VALIDACIÓN OK] {descripcion}: {e}")


def main():
    # La demo usa su propia base y la recrea en cada ejecución.
    # La base real de la aplicación es veterinaria.db (Conexion() sin parámetros).
    RUTA_DB_DEMO.unlink(missing_ok=True)
    repo = Repositorio(Conexion(RUTA_DB_DEMO)).cargar()
    clientes = ServicioClientes(repo)
    atencion = ServicioAtencion(repo)
    laboratorio = ServicioLaboratorio(repo)

    # Fecha base: mañana a las 9:00 (no se pueden agendar turnos en el pasado)
    t0 = datetime.combine(date.today() + timedelta(days=1), time(9, 0))

    titulo("SISTEMA DE RED DE CLÍNICAS Y DERIVACIÓN DE LABORATORIO")

    # -------------------------------------------------------------------------
    # 0. DATOS MAESTROS: clínicas, laboratorio, profesionales y conservadoras
    # -------------------------------------------------------------------------
    sede_centro = atencion.alta_clinica("Sede Centro", "Av. Colón 1200")
    sede_norte = atencion.alta_clinica("Sede Norte", "Av. Rafael Núñez 4500")
    lab_central = laboratorio.alta_laboratorio("Laboratorio Central", "Bv. San Juan 800")

    dra_lopez = atencion.alta_veterinario(
        "28111222", "Mariana", "López", "351-1112222", "mlopez@vet.com", "5541", "Clínica general", sede_centro, "Mañana"
    )
    dr_gomez = atencion.alta_veterinario(
        "30222333", "Esteban", "Gómez", "351-2223333", "egomez@vet.com", "4120", "Cirugía", sede_norte, "Mañana"
    )
    bioq_tevez = laboratorio.alta_bioquimico(
        "25333444", "Carlos", "Tevez", "351-3334444", "ctevez@lab.com", "8812", lab_central
    )

    conservadora_12 = laboratorio.alta_conservadora(12, capacidad_maxima=10, temperatura_objetivo="4°C")
    conservadora_15 = laboratorio.alta_conservadora(15, capacidad_maxima=4, temperatura_objetivo="4°C")

    # -------------------------------------------------------------------------
    # 1 y 2. ADMINISTRAR CLIENTES Y MASCOTAS
    # -------------------------------------------------------------------------
    seccion("1. Clientes y mascotas")
    clientes.alta_cliente("35890123", "Laura", "Fernández", "351-4567890", "laura.fernandez@email.com")
    clientes.alta_cliente("40111222", "Martín", "Ruiz", "351-9876543", "martin.ruiz@email.com")

    simon = clientes.alta_mascota("Simón", "Canino", "Golden Retriever", date(2021, 6, 15), 31.5, "35890123")
    mora = clientes.alta_mascota("Mora", "Felino", "Europeo", date(2022, 2, 1), 4.2, "35890123")
    rocco = clientes.alta_mascota("Rocco", "Canino", "Mestizo", date(2019, 9, 3), 18.0, "40111222")

    clientes.registrar_vacuna(simon.id_mascota, "Antirrábica", date(2026, 3, 10))
    clientes.registrar_vacuna(simon.id_mascota, "Séxtuple", date(2026, 3, 10))
    clientes.registrar_vacuna(rocco.id_mascota, "Antirrábica", date(2025, 11, 2))

    clientes.modificar_cliente("40111222", telefono="351-5550000")
    print(clientes.buscar_cliente("35890123"))
    print(clientes.buscar_cliente("40111222"))

    intentar("Mascota sin responsable",
             lambda: clientes.alta_mascota("Toby", "Canino", "Beagle", date(2023, 1, 1), 10.0, "99999999"))
    intentar("Baja de cliente con mascotas activas", lambda: clientes.baja_cliente("35890123"))

    # -------------------------------------------------------------------------
    # AGENDA: turnos sin superposición
    # -------------------------------------------------------------------------
    seccion("Agenda de turnos")
    turno_simon = atencion.agendar_turno(t0, "Consulta", simon, dra_lopez, "Cuadro febril y decaimiento general")
    turno_mora = atencion.agendar_turno(t0 + timedelta(minutes=45), "Control", mora, dra_lopez, "Control anual")
    for turno in dra_lopez.agenda_del_dia(t0.date()):
        print(turno)
    intentar("Turno superpuesto",
             lambda: atencion.agendar_turno(t0 + timedelta(minutes=15), "Consulta", rocco, dra_lopez, "Consulta"))
    intentar("Turno fuera del horario del veterinario",
             lambda: atencion.agendar_turno(t0.replace(hour=14), "Control", rocco, dra_lopez, "Control"))
    intentar("Turno en una hora que ya pasó",
             lambda: atencion.agendar_turno(datetime.now() - timedelta(hours=1), "Control", rocco, dra_lopez, "Control"))
    libres = atencion.horarios_disponibles(dra_lopez, t0.date(), "Control")
    print(f"Horarios libres de {dra_lopez.nombre_completo()} para un control: {', '.join(h.strftime('%H:%M') for h in libres)}")

    # -------------------------------------------------------------------------
    # 3. CONSULTAS Y ÓRDENES DE DERIVACIÓN (con control de vacunas)
    # -------------------------------------------------------------------------
    seccion("3. Consultas médicas y derivaciones")
    # Atención de turnos: la mascota, el tipo y el motivo salen del turno
    consulta_simon = atencion.atender_turno(turno_simon, t0)
    atencion.registrar_diagnostico(
        consulta_simon,
        "Sospecha de infección bacteriana sistémica",
        "Antipirético y derivación urgente para hemograma y urocultivo",
    )
    print(consulta_simon)

    consulta_mora = atencion.atender_turno(turno_mora, t0 + timedelta(minutes=45))
    intentar("Atender dos veces el mismo turno", lambda: atencion.atender_turno(turno_mora, t0))
    atencion.registrar_diagnostico(consulta_mora, "Sin hallazgos", "Desparasitación interna")
    print(consulta_mora)
    if consulta_mora.vacunas_pendientes_detectadas:
        print(f"  [AVISO VACUNAS] {mora.nombre} tiene pendientes: {', '.join(consulta_mora.vacunas_pendientes_detectadas)}")

    # Urgencia: llega sin turno
    consulta_rocco = atencion.registrar_urgencia(t0, rocco, dr_gomez, "Decaimiento y pérdida de apetito")
    atencion.registrar_diagnostico(consulta_rocco, "Hepatomegalia a la palpación", "Hepatoprotector y biopsia hepática")
    print(consulta_rocco)
    if consulta_rocco.vacunas_pendientes_detectadas:
        print(f"  [AVISO VACUNAS] {rocco.nombre} tiene pendientes: {', '.join(consulta_rocco.vacunas_pendientes_detectadas)}")

    orden_simon = atencion.emitir_orden_derivacion(
        t0 + timedelta(minutes=20), consulta_simon, "Panel infeccioso", lab_central
    )
    orden_rocco = atencion.emitir_orden_derivacion(
        t0 + timedelta(minutes=25), consulta_rocco, "Histopatología", lab_central
    )

    # -------------------------------------------------------------------------
    # 4. EXTRACCIÓN Y EMPAQUETADO (genera remito y precinto)
    # -------------------------------------------------------------------------
    seccion("4. Extracción y empaquetado - Sede Centro")
    sangre = laboratorio.registrar_extraccion("Sangre con EDTA", t0 + timedelta(minutes=40), orden_simon)
    orina = laboratorio.registrar_extraccion("Orina por cistocentesis", t0 + timedelta(minutes=45), orden_simon)

    remito_centro = laboratorio.empaquetar(t0 + timedelta(hours=1), sede_centro, lab_central, conservadora_12, [sangre, orina])
    print(remito_centro)

    intentar("Usar una conservadora que ya está en otro remito",
             lambda: laboratorio.empaquetar(t0 + timedelta(hours=1), sede_centro, lab_central, conservadora_12, [orina]))

    # -------------------------------------------------------------------------
    # 5. CADENA DE ENVÍO
    # -------------------------------------------------------------------------
    seccion("5. Cadena de envío - Sede Centro")
    laboratorio.despachar(remito_centro, t0 + timedelta(hours=1, minutes=30), "Logística Andina - Móvil 3")
    laboratorio.registrar_evento_traslado(remito_centro, t0 + timedelta(hours=2), "Control Ruta 9", "Sin novedad", "Paso por punto de control")
    intentar("Agregar muestras a un remito ya despachado",
             lambda: remito_centro.agregar_muestra(sangre))

    # -------------------------------------------------------------------------
    # 6. RECEPCIÓN CON INSPECCIÓN DEL PRECINTO (intacto)
    # -------------------------------------------------------------------------
    seccion("6. Recepción en laboratorio - precinto intacto")
    laboratorio.recibir_remito(remito_centro, t0 + timedelta(hours=3), precinto_intacto=True, receptor=bioq_tevez)
    print(remito_centro)
    intentar("Recibir dos veces el mismo remito",
             lambda: laboratorio.recibir_remito(remito_centro, t0 + timedelta(hours=4), True, bioq_tevez))

    # -------------------------------------------------------------------------
    # 7. RESULTADOS Y COMPROBANTE
    # -------------------------------------------------------------------------
    seccion("7. Resultados y comprobante de atención")
    laboratorio.registrar_resultado(
        t0 + timedelta(hours=6), sangre,
        "Leucocitos elevados, hematocrito normal. Infección confirmada: requiere tratamiento antibiótico.", bioq_tevez,
    )
    laboratorio.registrar_resultado(
        t0 + timedelta(hours=8), orina,
        "Densidad 1.025, proteínas en trazas, bacterias abundantes. Compatible con cistitis bacteriana.", bioq_tevez,
    )
    comprobante = atencion.emitir_comprobante(
        t0 + timedelta(hours=9), consulta_simon
    )
    print(comprobante)

    # -------------------------------------------------------------------------
    # CASO DE FALLA: precinto roto -> muestra rechazada -> re-extracción
    # -------------------------------------------------------------------------
    titulo("CASO DE FALLA EN LA CADENA DE CUSTODIA - Sede Norte")
    biopsia = laboratorio.registrar_extraccion("Biopsia de tejido", t0 + timedelta(minutes=50), orden_rocco)
    remito_norte = laboratorio.empaquetar(t0 + timedelta(hours=1), sede_norte, lab_central, conservadora_15, [biopsia])
    laboratorio.despachar(remito_norte, t0 + timedelta(hours=2), "Logística Andina - Móvil 7")
    laboratorio.registrar_evento_traslado(remito_norte, t0 + timedelta(hours=3), "Ruta 19 km 12", "Golpe o caída de la conservadora", "Bache fuerte")

    print("\nRecepción: el bioquímico detecta el precinto violado.")
    laboratorio.recibir_remito(
        remito_norte, t0 + timedelta(hours=5), precinto_intacto=False, receptor=bioq_tevez,
        observaciones="Precinto cortado y tapa mal cerrada",
    )
    print(remito_norte)

    intentar("Analizar una muestra rechazada",
             lambda: laboratorio.registrar_resultado(t0 + timedelta(hours=6), biopsia, "Informe", bioq_tevez))

    print("\nSe coordina una nueva extracción:")
    biopsia_2 = laboratorio.solicitar_reextraccion(biopsia, t0 + timedelta(days=1))
    remito_norte_2 = laboratorio.empaquetar(t0 + timedelta(days=1, hours=1), sede_norte, lab_central, conservadora_15, [biopsia_2])
    laboratorio.despachar(remito_norte_2, t0 + timedelta(days=1, hours=1, minutes=30), "Logística Andina - Móvil 7")
    laboratorio.recibir_remito(remito_norte_2, t0 + timedelta(days=1, hours=4), True, bioq_tevez)
    laboratorio.registrar_resultado(
        t0 + timedelta(days=2), biopsia_2,
        "Hepatitis crónica leve. Sin evidencia de neoplasia.", bioq_tevez,
    )

    # -------------------------------------------------------------------------
    # RECHAZO PUNTUAL: precinto intacto pero una muestra llega mal
    # -------------------------------------------------------------------------
    titulo("RECHAZO PUNTUAL DE UNA MUESTRA - Sede Centro")
    orden_control = atencion.emitir_orden_derivacion(t0 + timedelta(days=3), consulta_mora, "Hemograma", lab_central)
    sangre_mora = laboratorio.registrar_extraccion("Sangre con EDTA", t0 + timedelta(days=3), orden_control)
    suero_mora = laboratorio.registrar_extraccion("Suero (sangre sin anticoagulante)", t0 + timedelta(days=3), orden_control)
    remito_centro_2 = laboratorio.empaquetar(t0 + timedelta(days=3, hours=1), sede_centro, lab_central, conservadora_12,
                                             [sangre_mora, suero_mora])
    laboratorio.despachar(remito_centro_2, t0 + timedelta(days=3, hours=2), "Logística Andina - Móvil 3")
    laboratorio.recibir_remito(remito_centro_2, t0 + timedelta(days=3, hours=3), True, bioq_tevez,
                               rechazos={suero_mora.codigo_muestra: ("Recipiente roto o derramado", "")})
    print(remito_centro_2, "| Con observaciones:", remito_centro_2.recibido_con_observaciones())
    intentar("Rechazar con un motivo que no existe",
             lambda: laboratorio.rechazar_muestra(sangre_mora, "Porque sí", "", bioq_tevez, t0 + timedelta(days=3, hours=4)))
    laboratorio.rechazar_muestra(sangre_mora, "Volumen insuficiente", "", bioq_tevez, t0 + timedelta(days=3, hours=4))
    print(sangre_mora, "|", sangre_mora.motivo_rechazo())

    # -------------------------------------------------------------------------
    # TRAZABILIDAD Y VISTAS POR ROL
    # -------------------------------------------------------------------------
    seccion(f"Trazabilidad de la muestra {sangre.codigo_muestra} (sangre de Simón)")
    for registro in sangre.obtener_historial():
        print(registro)

    seccion("Cadena de envío del remito rechazado")
    for evento in remito_norte.eventos:
        print(evento)

    seccion("Lo que conoce cada rol")
    laura = clientes.buscar_cliente("35890123")
    print(f"{laura.nombre_completo()} (cliente) -> sus mascotas: {[m.nombre for m in laura.mascotas_activas()]}")
    print(f"{dra_lopez.nombre_completo()} (veterinaria) -> pacientes atendidos: {[m.nombre for m in dra_lopez.mascotas_atendidas()]}")
    print(f"{bioq_tevez.nombre_completo()} (bioquímico) -> remitos recibidos: {[r.numero for r in bioq_tevez.remitos_recibidos]}, "
          f"resultados firmados: {len(bioq_tevez.resultados_firmados)}")

    # -------------------------------------------------------------------------
    # REPORTES
    # -------------------------------------------------------------------------
    titulo("REPORTES")
    imprimir_reportes(repo)

    # -------------------------------------------------------------------------
    # PERSISTENCIA: se cierra la conexión y se vuelve a leer todo desde el archivo
    # -------------------------------------------------------------------------
    Conexion.cerrar()
    titulo("DATOS RELEÍDOS DESDE LA BASE (simula cerrar y volver a abrir el programa)")
    repo_releido = Repositorio(Conexion(RUTA_DB_DEMO)).cargar()
    print(f"Clientes: {len(repo_releido.clientes)} | Mascotas: {len(repo_releido.mascotas)} | "
          f"Consultas: {len(repo_releido.consultas)} | Remitos: {len(repo_releido.remitos)} | "
          f"Muestras: {len(repo_releido.muestras)} | Resultados: {len(repo_releido.resultados)}")
    biopsia_releida = repo_releido.muestras[biopsia.codigo_muestra]
    print(f"{biopsia_releida} | reemplazada por {biopsia_releida.reemplazada_por.codigo_muestra}")
    print(f"Trazabilidad de {sangre.codigo_muestra} leída de la base:")
    for registro in repo_releido.muestras[sangre.codigo_muestra].obtener_historial():
        print(f"  {registro}")
    imprimir_reportes(repo_releido)
    Conexion.cerrar()


def imprimir_reportes(repo):
    generador = GeneradorReportes(
        list(repo.consultas.values()), list(repo.remitos.values()),
        list(repo.muestras.values()), list(repo.mascotas.values()),
    )

    seccion("1. Atenciones clínicas y derivaciones")
    rep = generador.reporte_atenciones_y_derivaciones()
    print(f"Total: {rep['total_consultas']} consultas | Derivadas: {rep['consultas_derivadas']} ({rep['tasa_derivacion_pct']}%)")
    for clinica, fila in rep["por_clinica"].items():
        print(f"  {clinica}: {fila['total']} atenciones {fila['por_tipo']} | "
              f"derivación {fila['tasa_derivacion_pct']}% | estudios: {fila['estudios']}")

    seccion("2. Muestras rechazadas por fallas en el transporte")
    rep = generador.reporte_muestras_rechazadas()
    print(f"Rechazadas: {rep['cantidad_rechazadas']} de {rep['total_muestras']} ({rep['tasa_rechazo_pct']}%)")
    print(f"  Por clínica: {rep['por_clinica']} | Por transportista: {rep['por_transportista']}")
    for d in rep["detalle"]:
        print(f"  * [{d['codigo']}] {d['tipo']} de {d['paciente']} | Remito #{d['remito']} | "
              f"{d['observacion_precinto']} | Re-extraída como: {d['reextraida']}")

    seccion("3. Facturación por clínica y servicios de laboratorio")
    rep = generador.reporte_facturacion_por_clinica(Tarifario.ARANCEL_ANALISIS_POR_MUESTRA)
    for clinica, f in rep["por_clinica"].items():
        print(f"  {clinica}: {f['cantidad_atenciones']} atenciones ${f['atenciones']:,.2f} | "
              f"{f['muestras_analizadas']} análisis ${f['laboratorio']:,.2f} | total ${f['total']:,.2f}")
    print(f"  TOTAL FACTURADO: ${rep['total_facturado']:,.2f} (atenciones ${rep['total_atenciones']:,.2f} + "
          f"laboratorio ${rep['total_laboratorio']:,.2f})")

    seccion("4. Tiempos de tránsito y procesamiento")
    rep = generador.reporte_tiempos()
    print(f"Tránsito promedio: {rep['promedio_transito_hs']} hs (máximo {rep['maximo_transito_hs']} hs)")
    print(f"Procesamiento promedio en laboratorio: {rep['promedio_procesamiento_hs']} hs")
    print(f"Demora total promedio (extracción -> resultado): {rep['promedio_total_hs']} hs")
    for ruta, horas in rep["promedio_por_ruta_hs"].items():
        print(f"  {ruta}: {horas} hs")


if __name__ == "__main__":
    main()
