from datetime import datetime, date

# Importación de clases desde los paquetes del proyecto
from Models.Clinica.Cliente import Cliente
from Models.Clinica.Mascota import Mascota
from Models.Clinica.Consulta import ConsultaMedica
from Models.Clinica.Vacuna import Vacuna

from Models.Laboratorio.OrdenDerivacion import OrdenDerivacion
from Models.Laboratorio.MuestraBiologica import MuestraBiologica
from Models.Laboratorio.ResultadoAnalisis import ResultadoAnalisis
from Models.Laboratorio.ObserverMuestra import AuditorTrazabilidad, NotificadorCliente

from Models.Logistica.Conservadora import Conservadora
from Models.Logistica.PrecintoSanitario import PrecintoSanitario
from Models.Logistica.RemitoBiologico import RemitoBiologico

# Importación del módulo de reportes
from Reports.GeneradorReportes import GeneradorReportes


def main():
    print("=" * 70)
    print("SISTEMA DE RED DE CLÍNICAS Y DERIVACIÓN DE LABORATORIO")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # 1. ATENCIÓN CLÍNICA: Registro de Cliente y Mascota
    # -------------------------------------------------------------------------
    print("\n--- 1. Registro Clínico y Consulta ---")
    responsable = Cliente(
        dni="35890123",
        nombre="Laura",
        apellido="Fernandez",
        telefono="351-4567890",
        email="laura.fernandez@email.com",
    )

    paciente = Mascota(
        id_mascota=101,
        nombre="Simón",
        especie="Canino",
        raza="Golden Retriever",
        fecha_nacimiento=date(2021, 6, 15),
        peso=31.5,
        responsable=responsable
    )

    # Registro de vacuna previa
    vacuna_antirrabica = Vacuna("Antirrábica", "LOTE-2026-X", date(2026, 3, 10))
    paciente.registrar_vacuna(vacuna_antirrabica)

    # Registro de atención médica
    consulta = ConsultaMedica(
        numero=501,
        fecha_hora=datetime.now(),
        mascota=paciente,
        veterinario="Dra. Mariana López (MP 5541)",
        motivo="Cuadro febril y decaimiento general",
        costo=18000.0
    )
    consulta.registrar_diagnostico(
        diagnostico="Sospecha de infección bacteriana sistémica",
        tratamiento="Antipirético y derivación urgente para hemograma y urocultivo"
    )
    print(consulta)

    # Consulta 2: Para enriquecer los reportes (atención común sin derivación)
    consulta_rutina = ConsultaMedica(
        numero=502,
        fecha_hora=datetime.now(),
        mascota=paciente,
        veterinario="Dr. Esteban Gómez (MP 4120)",
        motivo="Control posoperatorio rutinario",
        costo=12000.0
    )
    consulta_rutina.registrar_diagnostico("Evolución favorable", "Alta definitiva")

    # -------------------------------------------------------------------------
    # 2. LABORATORIO: Emisión de Orden y Extracción de Muestras
    # -------------------------------------------------------------------------
    print("\n--- 2. Emisión de Derivación y Extracción de Muestras ---")
    orden = OrdenDerivacion(
        numero=8001,
        fecha_emision=datetime.now(),
        consulta=consulta,
        tipo_estudio="Panel Infeccioso Completo",
        clinica="Clínica Veterinaria Central - Sede Centro"
    )

    muestra_a = MuestraBiologica(
        codigo_muestra="MUE-SANGRE-01",
        tipo_muestra="Sangre entera con EDTA",
        fecha_extraccion=datetime.now(),
        orden_derivacion=orden
    )

    muestra_b = MuestraBiologica(
        codigo_muestra="MUE-ORINA-02",
        tipo_muestra="Orina por cistocentesis",
        fecha_extraccion=datetime.now(),
        orden_derivacion=orden
    )

    orden.agregar_muestra(muestra_a)
    orden.agregar_muestra(muestra_b)

    # Configuración de Observadores (Patrón Observer)
    auditor = AuditorTrazabilidad()
    notificador = NotificadorCliente()

    for m in [muestra_a, muestra_b]:
        m.agregar_observador(auditor)
        m.agregar_observador(notificador)

    print(f"Estado inicial de {muestra_a.codigo_muestra}: {muestra_a.estado_actual.nombre()}")
    print(f"Estado inicial de {muestra_b.codigo_muestra}: {muestra_b.estado_actual.nombre()}")

    # -------------------------------------------------------------------------
    # 3. LOGÍSTICA: Empaquetado y Despacho en Remito Biológico
    # -------------------------------------------------------------------------
    print("\n--- 3. Logística: Empaquetado y Transporte ---")
    conservadora = Conservadora(numero=12, capacidad_maxima=10, temperatura_objetivo="4°C")
    precinto = PrecintoSanitario(codigo="PREC-2026-99A")

    remito = RemitoBiologico(
        numero=4401,
        fecha_emision=datetime.now(),
        clinica="Sede Centro",
        laboratorio="Laboratorio Central de Referencia",
        conservadora=conservadora,
        precinto=precinto
    )

    # Se empaquetan las muestras en el remito (transición a Empaquetada)
    remito.agregar_muestra(muestra_a)
    remito.agregar_muestra(muestra_b)

    # Despacho hacia laboratorio (transición a En tránsito)
    print("\nDespachando remito hacia el laboratorio central...")
    remito.despachar()

    # -------------------------------------------------------------------------
    # 4. CASO DE ÉXITO: Recepción con Precinto Intacto y Análisis (Sangre y Orina)
    # -------------------------------------------------------------------------
    print("\n--- 4. Escenario de Recepción Exitosa (Muestra A y B) ---")
    # Se simula recepción del remito con precinto sano
    remito.recibir_en_laboratorio(datetime.now())

    # Carga de resultados analíticos para muestra A (Sangre)
    resultado_sangre = ResultadoAnalisis(
        numero=1209,
        fecha_emision=datetime.now(),
        valores_obtenidos={"Glóbulos Blancos": "Elevados", "Hematocrito": "Normal"},
        observaciones="Infección confirmada. Requiere tratamiento antibiótico específico.",
        profesional="Bioq. Carlos Tevez (MP 8812)"
    )
    print("\nProcesando análisis de sangre (Muestra A)...")
    muestra_a.analizar(resultado_sangre)

    # Carga de resultados analíticos para muestra B (Orina)
    resultado_orina = ResultadoAnalisis(
        numero=1210,
        fecha_emision=datetime.now(),
        valores_obtenidos={"Densidad": 1.025, "Proteínas": "Trazas", "Bacterias": "Abundantes"},
        observaciones="Sedimento urinario activo compatible con cistitis bacteriana.",
        profesional="Bioq. Carlos Tevez (MP 8812)"
    )
    print("\nProcesando análisis de orina (Muestra B)...")
    muestra_b.analizar(resultado_orina)

    # -------------------------------------------------------------------------
    # 5. CASO DE FALLA: Precinto Roto y Bloqueo de Muestra Rechazada
    # -------------------------------------------------------------------------
    print("\n--- 5. Escenario de Falla de Cadena de Custodia (Demostración de Rechazo) ---")
    precinto_violado = PrecintoSanitario(codigo="PREC-ROTO-007")
    remito_accidentado = RemitoBiologico(
        numero=4402,
        fecha_emision=datetime.now(),
        clinica="Sede Norte",
        laboratorio="Laboratorio Central",
        conservadora=conservadora,
        precinto=precinto_violado
    )

    muestra_c = MuestraBiologica("MUE-BIOPSIA-03", "Biopsia Hepática", datetime.now(), orden)
    muestra_c.agregar_observador(auditor)
    muestra_c.agregar_observador(notificador)

    remito_accidentado.agregar_muestra(muestra_c)
    remito_accidentado.despachar()

    # Simulación: el precinto sufre una rotura durante el transporte
    print("\n[ALERTA DE TRANSPORTE] El precinto del remito sufrió una rotura accidental...")
    precinto_violado.alterado()

    # Recepción en laboratorio (verificación de precinto)
    remito_accidentado.recibir_en_laboratorio(datetime.now())

    # Validación de negocio: comprobar que el sistema impide procesar muestras rechazadas
    print("\nIntentando analizar la muestra rechazada (Debe arrojar excepción):")
    try:
        muestra_c.analizar(resultado_sangre)
    except ValueError as e:
        print(f"BLOQUEO CORRECTO DEL SISTEMA: {e}")

    # -------------------------------------------------------------------------
    # 6. TRAZABILIDAD INMUTABLE
    # -------------------------------------------------------------------------
    print("\n--- 6. Consulta de Trazabilidad Histórica Inmutable (Muestra A) ---")
    for registro in muestra_a.obtener_historial():
        print(registro)

    # -------------------------------------------------------------------------
    # 7. GENERADOR DE REPORTES Y AUDITORÍA
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("MÓDULO DE REPORTES ESTADÍSTICOS Y MÉTRICAS")
    print("=" * 70)

    lista_consultas = [consulta, consulta_rutina]
    lista_remitos = [remito, remito_accidentado]
    lista_muestras = [muestra_a, muestra_b, muestra_c]

    generador = GeneradorReportes(lista_consultas, lista_remitos, lista_muestras)

    print("\n--- 1. Reporte de Derivaciones Clínicas ---")
    rep_derivaciones = generador.reporte_atenciones_y_derivaciones()
    print(f"Total de consultas atendidas : {rep_derivaciones['total_consultas']}")
    print(f"Consultas con derivación    : {rep_derivaciones['consultas_derivadas']}")
    print(f"Tasa de derivación médica   : {rep_derivaciones['porcentaje_derivacion']}%")

    print("\n--- 2. Reporte de Muestras Rechazadas (Cadena de Custodia) ---")
    rep_rechazo = generador.reporte_muestras_rechazadas()
    print(f"Muestras procesadas totales : {rep_rechazo['total_muestras']}")
    print(f"Muestras rechazadas         : {rep_rechazo['cantidad_rechazadas']}")
    print(f"Tasa de rechazo             : {rep_rechazo['tasa_rechazo_pct']}%")
    for det in rep_rechazo['detalle']:
        print(f"  * [{det['codigo']}] Tipo: {det['tipo']} | Causa: {det['motivo_ultimo']}")

    print("\n--- 3. Reporte de Pacientes con Esquema Vacunatorio Pendiente ---")
    rep_vacunas = generador.reporte_vacunas_pendientes()
    if rep_vacunas:
        for p in rep_vacunas:
            print(f"Paciente: {p['paciente']} ({p['especie']}) | Responsable: {p['responsable']}")
            print(f"  Faltantes detectadas: {', '.join(p['vacunas_faltantes'])}")
    else:
        print("Todos los pacientes evaluados cuentan con su esquema de vacunación al día.")

    print("\n--- 4. Balance Financiero Consolidado ---")
    rep_balance = generador.reporte_balance_financiero(arancel_laboratorio_por_muestra=4500.0)
    print(f"Ingresos por atenciones clínicas   : ${rep_balance['ingresos_consultas']}")
    print(f"Muestras analizadas en laboratorio : {rep_balance['muestras_analizadas']}")
    print(f"Costos derivados de laboratorio    : ${rep_balance['costo_analisis_laboratorio']}")
    print(f"Balance neto de la red             : ${rep_balance['balance_neto']}")


if __name__ == "__main__":
    main()
