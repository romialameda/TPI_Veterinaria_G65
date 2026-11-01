from collections import Counter


class GeneradorReportes:
    """Métricas y reportes sobre la actividad clínica, logística y de laboratorio."""

    def __init__(self, consultas, remitos, muestras, mascotas):
        self.consultas = consultas
        self.remitos = remitos
        self.muestras = muestras
        self.mascotas = mascotas

    @staticmethod
    def _promedio(valores):
        return round(sum(valores) / len(valores), 2) if valores else None

    @staticmethod
    def _porcentaje(parte, total):
        return round(parte / total * 100, 2) if total > 0 else 0.0

    # -------------------------------------------------------------------------
    # Reporte 1: Atenciones clínicas y derivaciones, por clínica y tipo de atención
    # -------------------------------------------------------------------------
    def reporte_atenciones_y_derivaciones(self):
        por_clinica = {}
        for c in self.consultas:
            fila = por_clinica.setdefault(c.clinica.nombre, {
                "total": 0, "por_tipo": Counter(), "derivadas": 0, "estudios": Counter()
            })
            fila["total"] += 1
            fila["por_tipo"][c.tipo_atencion] += 1
            if c.tiene_derivacion():
                fila["derivadas"] += 1
                for orden in c.ordenes_derivacion:
                    fila["estudios"][orden.tipo_estudio] += 1

        for fila in por_clinica.values():
            fila["tasa_derivacion_pct"] = self._porcentaje(fila["derivadas"], fila["total"])
            fila["por_tipo"] = dict(fila["por_tipo"])
            fila["estudios"] = fila["estudios"].most_common()

        total = len(self.consultas)
        derivadas = sum(1 for c in self.consultas if c.tiene_derivacion())
        return {
            "total_consultas": total,
            "consultas_derivadas": derivadas,
            "tasa_derivacion_pct": self._porcentaje(derivadas, total),
            "por_clinica": por_clinica,
        }

    # -------------------------------------------------------------------------
    # Reporte 2: Muestras rechazadas por fallas en el transporte
    # -------------------------------------------------------------------------
    def reporte_muestras_rechazadas(self):
        rechazadas = [m for m in self.muestras if m.esta_rechazada()]
        por_clinica = Counter(m.orden_derivacion.clinica.nombre for m in rechazadas)
        por_transportista = Counter(m.remito.transportista for m in rechazadas if m.remito)

        detalle = [
            {
                "codigo": m.codigo_muestra,
                "tipo": m.tipo_muestra,
                "paciente": m.orden_derivacion.consulta.mascota.nombre,
                "remito": m.remito.numero if m.remito else None,
                "transportista": m.remito.transportista if m.remito else None,
                "observacion_precinto": m.remito.precinto.observaciones_inspeccion if m.remito else "",
                "reextraida": m.reemplazada_por.codigo_muestra if m.reemplazada_por else None,
            }
            for m in rechazadas
        ]
        return {
            "total_muestras": len(self.muestras),
            "cantidad_rechazadas": len(rechazadas),
            "tasa_rechazo_pct": self._porcentaje(len(rechazadas), len(self.muestras)),
            "por_clinica": dict(por_clinica),
            "por_transportista": dict(por_transportista),
            "detalle": detalle,
        }

    # -------------------------------------------------------------------------
    # Reporte 3: Tratamientos aplicados y vacunas pendientes por paciente
    # -------------------------------------------------------------------------
    def reporte_tratamientos_y_vacunas(self):
        filas = []
        for mascota in self.mascotas:
            if not mascota.activa:
                continue
            tratamientos = [
                {"fecha": c.fecha_hora, "diagnostico": c.diagnostico, "tratamiento": c.tratamiento}
                for c in mascota.historia_clinica() if c.tratamiento
            ]
            filas.append({
                "paciente": mascota.nombre,
                "especie": mascota.especie,
                "responsable": mascota.responsable.nombre_completo(),
                "contacto": mascota.responsable.telefono,
                "tratamientos": tratamientos,
                "vacunas_pendientes": mascota.vacunas_pendientes(),
            })
        return {
            "pacientes": filas,
            "con_vacunas_pendientes": sum(1 for f in filas if f["vacunas_pendientes"]),
        }

    # -------------------------------------------------------------------------
    # Reporte 4: Facturación desglosada por clínica y servicios de laboratorio
    # -------------------------------------------------------------------------
    def reporte_facturacion_por_clinica(self, arancel_laboratorio_por_muestra=4500.0):
        por_clinica = {}
        for c in self.consultas:
            fila = por_clinica.setdefault(c.clinica.nombre, {
                "ingresos_consultas": 0.0, "muestras_analizadas": 0, "muestras_rechazadas": 0
            })
            fila["ingresos_consultas"] += c.costo
            for orden in c.ordenes_derivacion:
                fila["muestras_analizadas"] += sum(1 for m in orden.muestras if m.esta_analizada())
                fila["muestras_rechazadas"] += sum(1 for m in orden.muestras if m.esta_rechazada())

        for fila in por_clinica.values():
            fila["costo_laboratorio"] = fila["muestras_analizadas"] * arancel_laboratorio_por_muestra
            fila["balance_neto"] = fila["ingresos_consultas"] - fila["costo_laboratorio"]

        return {
            "por_clinica": por_clinica,
            "total_ingresos": sum(f["ingresos_consultas"] for f in por_clinica.values()),
            "total_costo_laboratorio": sum(f["costo_laboratorio"] for f in por_clinica.values()),
            "total_balance_neto": sum(f["balance_neto"] for f in por_clinica.values()),
        }

    # -------------------------------------------------------------------------
    # Reporte 5: Tiempo promedio de tránsito y procesamiento de muestras
    # -------------------------------------------------------------------------
    def reporte_tiempos(self):
        por_ruta = {}
        for r in self.remitos:
            horas = r.horas_de_viaje()
            if horas is not None:
                por_ruta.setdefault(f"{r.clinica.nombre} -> {r.laboratorio.nombre}", []).append(horas)

        transito = [h for h in (m.horas_en_transito() for m in self.muestras) if h is not None]
        procesamiento = [h for h in (m.horas_de_procesamiento() for m in self.muestras) if h is not None]

        return {
            "promedio_transito_hs": self._promedio(transito),
            "maximo_transito_hs": round(max(transito), 2) if transito else None,
            "promedio_procesamiento_hs": self._promedio(procesamiento),
            "promedio_por_ruta_hs": {ruta: self._promedio(hs) for ruta, hs in por_ruta.items()},
        }
