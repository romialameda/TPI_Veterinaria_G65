import unicodedata
from collections import Counter
from datetime import date


class GeneradorReportes:
    """
    Métricas y reportes sobre la actividad clínica, logística y de laboratorio.
    Todos los reportes aceptan filtros opcionales: si un filtro es None, no se aplica.
    Las fechas de los filtros son objetos date (desde y hasta inclusive).
    """

    def __init__(self, consultas, remitos, muestras, mascotas, turnos=None):
        self.consultas = consultas
        self.remitos = remitos
        self.muestras = muestras
        self.mascotas = mascotas
        self.turnos = turnos or []

    # =========================================================================
    # Utilidades
    # =========================================================================
    @staticmethod
    def _promedio(valores):
        return round(sum(valores) / len(valores), 2) if valores else None

    @staticmethod
    def _porcentaje(parte, total):
        return round(parte / total * 100, 2) if total > 0 else 0.0

    @staticmethod
    def _normalizar(texto):
        """Minúsculas y sin tildes, para que 'Gómez' y 'gomez' coincidan."""
        sin_tildes = unicodedata.normalize("NFD", str(texto))
        return "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn").strip().casefold()

    @classmethod
    def _coincide_filtro(cls, valor, filtro):
        """Filtro de texto: coincide si el texto buscado está contenido (sin importar tildes ni mayúsculas)."""
        if filtro is None or str(filtro).strip() == "":
            return True
        return cls._normalizar(filtro) in cls._normalizar(valor)

    @staticmethod
    def _en_rango(fecha, desde, hasta):
        if fecha is None:
            return desde is None and hasta is None
        dia = fecha.date() if hasattr(fecha, "date") else fecha
        return (desde is None or dia >= desde) and (hasta is None or dia <= hasta)

    @classmethod
    def _coincide_veterinario(cls, vet, filtro):
        """Acepta la matrícula exacta o una parte del nombre."""
        if filtro is None or str(filtro).strip() == "":
            return True
        return str(filtro).strip() == vet.matricula or cls._coincide_filtro(vet.nombre_completo(), filtro)

    @staticmethod
    def _coincide_clinica(clinica, filtro):
        """Acepta el id de la clínica o su nombre exacto."""
        if filtro is None or str(filtro).strip() == "":
            return True
        return str(filtro).strip() in (str(clinica.id_clinica), clinica.nombre)

    def _consultas_filtradas(self, desde=None, hasta=None, clinica=None, veterinario=None, especie=None,
                             tipo_atencion=None, responsable=None, paciente=None):
        """responsable: DNI del cliente. paciente: id de la mascota (evita confundir mascotas con el mismo nombre)."""
        return [
            c for c in self.consultas
            if self._en_rango(c.fecha_hora, desde, hasta)
            and self._coincide_clinica(c.clinica, clinica)
            and self._coincide_veterinario(c.veterinario, veterinario)
            and self._coincide_filtro(c.mascota.especie, especie)
            and (tipo_atencion is None or c.tipo_atencion == tipo_atencion)
            and (responsable is None or c.mascota.responsable.dni == str(responsable))
            and (paciente is None or str(c.mascota.id_mascota) == str(paciente))
        ]

    @staticmethod
    def _ordenar(filas, ordenar_por, descendente, campos_ordenables):
        """Ordena la lista de filas por un campo; los valores vacíos quedan siempre al final."""
        if ordenar_por is None:
            return filas
        if ordenar_por not in campos_ordenables:
            raise ValueError(f"Campo de orden inválido: {ordenar_por}. Opciones: {', '.join(sorted(campos_ordenables))}")
        con_valor = [f for f in filas if f[ordenar_por] is not None]
        sin_valor = [f for f in filas if f[ordenar_por] is None]
        con_valor.sort(
            key=lambda f: f[ordenar_por].casefold() if isinstance(f[ordenar_por], str) else f[ordenar_por],
            reverse=descendente,
        )
        return con_valor + sin_valor

    # =========================================================================
    # Reporte 1: Atenciones clínicas y derivaciones
    # =========================================================================
    def reporte_atenciones_y_derivaciones(self, desde=None, hasta=None, clinica=None, veterinario=None,
                                          especie=None, tipo_atencion=None, responsable=None, paciente=None):
        consultas = self._consultas_filtradas(desde, hasta, clinica, veterinario, especie, tipo_atencion,
                                              responsable, paciente)

        por_clinica = {}
        por_veterinario = {}
        estudios = Counter()
        for c in consultas:
            fila = por_clinica.setdefault(c.clinica.nombre, {
                "total": 0, "por_tipo": Counter(), "derivadas": 0, "estudios": Counter()
            })
            vet = por_veterinario.setdefault(c.veterinario.matricula, {
                "veterinario": c.veterinario.nombre_completo(), "clinica": c.clinica.nombre, "total": 0, "derivadas": 0
            })
            fila["total"] += 1
            vet["total"] += 1
            fila["por_tipo"][c.tipo_atencion] += 1
            if c.tiene_derivacion():
                fila["derivadas"] += 1
                vet["derivadas"] += 1
                for orden in c.ordenes_derivacion:
                    fila["estudios"][orden.tipo_estudio] += 1
                    estudios[orden.tipo_estudio] += 1

        for fila in list(por_clinica.values()) + list(por_veterinario.values()):
            fila["tasa_derivacion_pct"] = self._porcentaje(fila["derivadas"], fila["total"])
        for fila in por_clinica.values():
            fila["por_tipo"] = dict(fila["por_tipo"])
            fila["estudios"] = fila["estudios"].most_common()

        derivadas = sum(1 for c in consultas if c.tiene_derivacion())
        return {
            "total_consultas": len(consultas),
            "consultas_derivadas": derivadas,
            "tasa_derivacion_pct": self._porcentaje(derivadas, len(consultas)),
            "por_clinica": por_clinica,
            "por_tipo": dict(Counter(c.tipo_atencion for c in consultas)),
            "por_veterinario": sorted(por_veterinario.values(), key=lambda v: -v["total"]),
            "por_estudio": estudios.most_common(),
            "detalle": [
                {
                    "fecha": c.fecha_hora, "clinica": c.clinica.nombre, "veterinario": c.veterinario.nombre_completo(),
                    "paciente": c.mascota.nombre, "responsable": c.mascota.responsable.nombre_completo(),
                    "especie": c.mascota.especie, "tipo": c.tipo_atencion,
                    "motivo": c.motivo, "derivada": c.tiene_derivacion(),
                    "estudios": ", ".join(o.tipo_estudio for o in c.ordenes_derivacion),
                }
                for c in sorted(consultas, key=lambda c: c.fecha_hora, reverse=True)
            ],
        }

    # =========================================================================
    # Reporte 2: Muestras rechazadas por fallas en el transporte
    # =========================================================================
    @staticmethod
    def _causa_rechazo(muestra):
        """Agrupa el motivo: precinto roto (todo el contenedor) o el motivo puntual de la muestra."""
        motivo = muestra.motivo_rechazo() or ""
        if "precinto" in motivo:
            return "Precinto roto (todo el contenedor)"
        return motivo.split(": ", 1)[-1].split(" (")[0] or "Sin motivo"

    def reporte_muestras_rechazadas(self, especie=None, veterinario=None, contenedor=None, ordenar_por=None,
                                    descendente=False, desde=None, hasta=None, clinica=None):
        """Lista muestras rechazadas con filtros opcionales y orden configurable.

        ``contenedor`` corresponde al número de la conservadora asociada al remito.
        ``desde``/``hasta`` filtran por fecha de extracción de la muestra.
        ``ordenar_por`` admite: codigo, tipo, paciente, especie, veterinario, contenedor o fecha.
        """
        muestras_filtradas = []
        for muestra in self.muestras:
            consulta = muestra.orden_derivacion.consulta
            numero_contenedor = (
                muestra.remito.conservadora.numero
                if muestra.remito and muestra.remito.conservadora
                else None
            )
            if not self._coincide_filtro(consulta.mascota.especie, especie):
                continue
            if not self._coincide_veterinario(consulta.veterinario, veterinario):
                continue
            if contenedor is not None and str(contenedor).strip() != "" and str(numero_contenedor) != str(contenedor).strip():
                continue
            if not self._coincide_clinica(consulta.clinica, clinica):
                continue
            if not self._en_rango(muestra.fecha_extraccion, desde, hasta):
                continue
            muestras_filtradas.append(muestra)

        rechazadas = [m for m in muestras_filtradas if m.esta_rechazada()]
        por_clinica = Counter(m.orden_derivacion.clinica.nombre for m in rechazadas)
        por_transportista = Counter(m.remito.transportista for m in rechazadas if m.remito)
        por_contenedor = Counter(f"#{m.remito.conservadora.numero}" for m in rechazadas if m.remito)
        por_causa = Counter(self._causa_rechazo(m) for m in rechazadas)

        detalle = [
            {
                "codigo": m.codigo_muestra,
                "tipo": m.tipo_muestra,
                "fecha": m.remito.fecha_recepcion if m.remito else None,
                "paciente": m.orden_derivacion.consulta.mascota.nombre,
                "especie": m.orden_derivacion.consulta.mascota.especie,
                "veterinario": m.orden_derivacion.consulta.veterinario.nombre_completo(),
                "contenedor": m.remito.conservadora.numero if m.remito else None,
                "remito": m.remito.numero if m.remito else None,
                "transportista": m.remito.transportista if m.remito else None,
                "motivo": m.motivo_rechazo(),
                "observacion_precinto": m.remito.precinto.observaciones_inspeccion if m.remito else "",
                "novedades_traslado": ", ".join(e.novedad for e in m.remito.novedades_del_traslado()) if m.remito else "",
                "reextraida": m.reemplazada_por.codigo_muestra if m.reemplazada_por else None,
            }
            for m in rechazadas
        ]
        campos_ordenables = {"codigo", "tipo", "paciente", "especie", "veterinario", "contenedor", "fecha"}
        detalle = self._ordenar(detalle, ordenar_por, descendente, campos_ordenables)

        return {
            "total_muestras": len(muestras_filtradas),
            "cantidad_rechazadas": len(rechazadas),
            "tasa_rechazo_pct": self._porcentaje(len(rechazadas), len(muestras_filtradas)),
            "por_clinica": dict(por_clinica),
            "por_transportista": dict(por_transportista),
            "por_contenedor": dict(por_contenedor),
            "por_causa": dict(por_causa),
            "detalle": detalle,
        }

    # =========================================================================
    # Reporte 3: Facturación desglosada por clínica y servicios de laboratorio
    # =========================================================================
    def reporte_facturacion_por_clinica(self, arancel_analisis_por_muestra=4500.0, desde=None, hasta=None,
                                        clinica=None, veterinario=None):
        """
        Lo facturado a los clientes, desglosado por clínica en:
        - atenciones (consultas, controles y urgencias, con su precio fijo)
        - servicios de laboratorio (cada muestra analizada se cobra al cliente con un arancel fijo)
        """
        consultas = self._consultas_filtradas(desde, hasta, clinica, veterinario)
        por_clinica = {}
        por_tipo = Counter()
        por_estudio = Counter()
        for c in consultas:
            fila = por_clinica.setdefault(c.clinica.nombre, {
                "cantidad_atenciones": 0, "atenciones": 0.0, "muestras_analizadas": 0, "laboratorio": 0.0
            })
            fila["cantidad_atenciones"] += 1
            fila["atenciones"] += c.costo
            por_tipo[c.tipo_atencion] += c.costo
            for orden in c.ordenes_derivacion:
                analizadas = sum(1 for m in orden.muestras if m.esta_analizada())
                fila["muestras_analizadas"] += analizadas
                fila["laboratorio"] += analizadas * arancel_analisis_por_muestra
                por_estudio[orden.tipo_estudio] += analizadas * arancel_analisis_por_muestra

        for fila in por_clinica.values():
            fila["total"] = fila["atenciones"] + fila["laboratorio"]

        total_atenciones = sum(f["atenciones"] for f in por_clinica.values())
        total_laboratorio = sum(f["laboratorio"] for f in por_clinica.values())
        return {
            "por_clinica": por_clinica,
            "por_tipo_atencion": dict(por_tipo),
            "laboratorio_por_estudio": {e: v for e, v in por_estudio.most_common() if v},
            "arancel_analisis_por_muestra": arancel_analisis_por_muestra,
            "total_atenciones": total_atenciones,
            "total_laboratorio": total_laboratorio,
            "total_facturado": total_atenciones + total_laboratorio,
        }

    # =========================================================================
    # Reporte 4: Tiempo promedio de tránsito y procesamiento de muestras
    # =========================================================================
    def reporte_tiempos(self, desde=None, hasta=None, clinica=None, tipo_muestra=None, tipo_estudio=None):
        muestras = [
            m for m in self.muestras
            if self._en_rango(m.fecha_extraccion, desde, hasta)
            and self._coincide_clinica(m.orden_derivacion.clinica, clinica)
            and (tipo_muestra is None or m.tipo_muestra == tipo_muestra)
            and (tipo_estudio is None or m.orden_derivacion.tipo_estudio == tipo_estudio)
        ]
        remitos = {m.remito for m in muestras if m.remito}

        por_ruta = {}
        for r in remitos:
            horas = r.horas_de_viaje()
            if horas is not None:
                por_ruta.setdefault(f"{r.clinica.nombre} -> {r.laboratorio.nombre}", []).append(horas)

        transito = [h for h in (m.horas_en_transito() for m in muestras) if h is not None]
        procesamiento = [h for h in (m.horas_de_procesamiento() for m in muestras) if h is not None]
        total = [h for h in (m.horas_hasta_resultado() for m in muestras) if h is not None]
        por_estudio, total_por_estudio = {}, {}
        for m in muestras:
            if m.horas_de_procesamiento() is not None:
                por_estudio.setdefault(m.orden_derivacion.tipo_estudio, []).append(m.horas_de_procesamiento())
            if m.horas_hasta_resultado() is not None:
                total_por_estudio.setdefault(m.orden_derivacion.tipo_estudio, []).append(m.horas_hasta_resultado())

        return {
            "promedio_transito_hs": self._promedio(transito),
            "maximo_transito_hs": round(max(transito), 2) if transito else None,
            "promedio_procesamiento_hs": self._promedio(procesamiento),
            "promedio_por_ruta_hs": {ruta: self._promedio(hs) for ruta, hs in por_ruta.items()},
            "procesamiento_por_estudio_hs": {e: self._promedio(hs) for e, hs in por_estudio.items()},
            # Demora total = desde la extracción hasta el resultado (lo que espera el cliente)
            "promedio_total_hs": self._promedio(total),
            "demora_total_por_estudio_hs": {e: self._promedio(hs) for e, hs in total_por_estudio.items()},
            "detalle": [
                {
                    "codigo": m.codigo_muestra, "tipo": m.tipo_muestra, "estudio": m.orden_derivacion.tipo_estudio,
                    "clinica": m.orden_derivacion.clinica.nombre, "estado": m.estado_actual.nombre(),
                    "horas_transito": round(m.horas_en_transito(), 2) if m.horas_en_transito() is not None else None,
                    "horas_procesamiento": round(m.horas_de_procesamiento(), 2) if m.horas_de_procesamiento() is not None else None,
                    "horas_total": round(m.horas_hasta_resultado(), 2) if m.horas_hasta_resultado() is not None else None,
                }
                for m in sorted(muestras, key=lambda m: m.fecha_extraccion, reverse=True)
            ],
        }

    # =========================================================================
    # Reporte 5: Turnos y asistencia
    # =========================================================================
    DIAS_SEMANA = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo")

    def reporte_turnos(self, desde=None, hasta=None, clinica=None, veterinario=None, tipo=None, estado=None, hoy=None):
        """
        Turnos dados por recepción y qué pasó con cada uno: Atendido, Ausente (no vino), Cancelado o Pendiente.
        Sirve para ver el ausentismo y la carga de cada veterinario. También cuenta las urgencias (sin turno).
        """
        hoy = hoy or date.today()
        turnos = [
            t for t in self.turnos
            if self._en_rango(t.inicio, desde, hasta)
            and self._coincide_clinica(t.veterinario.clinica, clinica)
            and self._coincide_veterinario(t.veterinario, veterinario)
            and (tipo is None or t.tipo == tipo)
            and (estado is None or t.estado(hoy) == estado)
        ]
        por_estado = Counter(t.estado(hoy) for t in turnos)

        por_veterinario = {}
        for t in turnos:
            v = t.veterinario
            fila = por_veterinario.setdefault(v.matricula, {
                "veterinario": v.nombre_completo(), "clinica": v.clinica.nombre, "turno_laboral": v.turno_laboral,
                "total": 0, "Atendido": 0, "Ausente": 0, "Cancelado": 0, "Pendiente": 0,
            })
            fila["total"] += 1
            fila[t.estado(hoy)] += 1
        for fila in por_veterinario.values():
            fila["asistencia_pct"] = self._porcentaje(fila["Atendido"], fila["Atendido"] + fila["Ausente"])

        por_dia = Counter(self.DIAS_SEMANA[t.inicio.weekday()] for t in turnos if not t.cancelado)
        urgencias = [
            c for c in self._consultas_filtradas(desde, hasta, clinica, veterinario, tipo_atencion="Urgencia")
        ]
        atendidos, ausentes = por_estado.get("Atendido", 0), por_estado.get("Ausente", 0)
        return {
            "total_turnos": len(turnos),
            "por_estado": {e: por_estado.get(e, 0) for e in ("Atendido", "Ausente", "Cancelado", "Pendiente")},
            "asistencia_pct": self._porcentaje(atendidos, atendidos + ausentes),
            "ausentismo_pct": self._porcentaje(ausentes, atendidos + ausentes),
            "urgencias_sin_turno": len(urgencias),
            "por_veterinario": sorted(por_veterinario.values(), key=lambda f: (f["clinica"], f["turno_laboral"] != "Mañana")),
            "por_dia_semana": {d: por_dia[d] for d in self.DIAS_SEMANA if por_dia.get(d)},
            "detalle": [
                {
                    "inicio": t.inicio, "fin": t.fin, "clinica": t.veterinario.clinica.nombre,
                    "veterinario": t.veterinario.nombre_completo(), "paciente": t.mascota.nombre,
                    "responsable": t.mascota.responsable.nombre_completo(), "tipo": t.tipo, "motivo": t.motivo,
                    "estado": t.estado(hoy),
                }
                for t in sorted(turnos, key=lambda t: t.inicio, reverse=True)
            ],
        }
