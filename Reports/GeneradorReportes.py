class GeneradorReportes:
    """
    Módulo encargado de computar métricas y reportes no triviales
    sobre la actividad clínica, logística y de laboratorio.
    """
    def __init__(self, consultas, remitos, muestras):
        self.consultas = consultas
        self.remitos = remitos
        self.muestras = muestras

    # -------------------------------------------------------------------------
    # Reporte 1: Tasa de derivación por clínica / consultas totales
    # -------------------------------------------------------------------------
    def reporte_atenciones_y_derivaciones(self):
        total_consultas = len(self.consultas)
        derivadas = [c for c in self.consultas if c.tiene_derivacion()]
        porcentaje = (len(derivadas) / total_consultas * 100) if total_consultas > 0 else 0.0
        
        return {
            "total_consultas": total_consultas,
            "consultas_derivadas": len(derivadas),
            "porcentaje_derivacion": round(porcentaje, 2)
        }

    # -------------------------------------------------------------------------
    # Reporte 2: Índice y causas de muestras biológicas rechazadas
    # -------------------------------------------------------------------------
    def reporte_muestras_rechazadas(self):
        total_muestras = len(self.muestras)
        rechazadas = [m for m in self.muestras if m.estado_actual.nombre() == "Rechazada"]
        porcentaje_rechazo = (len(rechazadas) / total_muestras * 100) if total_muestras > 0 else 0.0
        
        detalle_rechazos = [
            {
                "codigo": m.codigo_muestra,
                "tipo": m.tipo_muestra,
                "motivo_ultimo": m.obtener_historial()[-1].motivo if m.obtener_historial() else "Desconocido"
            }
            for m in rechazadas
        ]

        return {
            "total_muestras": total_muestras,
            "cantidad_rechazadas": len(rechazadas),
            "tasa_rechazo_pct": round(porcentaje_rechazo, 2),
            "detalle": detalle_rechazos
        }

    # -------------------------------------------------------------------------
    # Reporte 3: Control sanitario: pacientes con vacunas obligatorias pendientes
    # -------------------------------------------------------------------------
    def reporte_vacunas_pendientes(self):
        pacientes_incompletos = []
        for c in self.consultas:
            # Evalúa mediante el método de control de la consulta médica
            if hasattr(c, "verificar_vacunacion_obligatoria"):
                faltantes = c.verificar_vacunacion_obligatoria()
                if faltantes:
                    pacientes_incompletos.append({
                        "paciente": c.mascota.nombre,
                        "especie": c.mascota.especie,
                        "responsable": f"{c.mascota.responsable.nombre} {c.mascota.responsable.apellido}",
                        "vacunas_faltantes": faltantes
                    })
        return pacientes_incompletos

    # -------------------------------------------------------------------------
    # Reporte 4: Facturación desglosada (Ingresos clínicas vs costos laboratorio)
    # -------------------------------------------------------------------------
    def reporte_balance_financiero(self, arancel_laboratorio_por_muestra=4500.0):
        ingresos_consultas = sum(c.costo for c in self.consultas)
        # Costo originado por procesar muestras derivadas
        muestras_procesadas = sum(
            1 for m in self.muestras if m.estado_actual.nombre() == "Analizada"
        )
        costo_laboratorio = muestras_procesadas * arancel_laboratorio_por_muestra
        balance_neto = ingresos_consultas - costo_laboratorio

        return {
            "ingresos_consultas": ingresos_consultas,
            "costo_analisis_laboratorio": costo_laboratorio,
            "balance_neto": balance_neto,
            "muestras_analizadas": muestras_procesadas
        }