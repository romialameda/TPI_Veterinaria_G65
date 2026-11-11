"""
Convierte los objetos del modelo a diccionarios, que FastAPI devuelve como JSON al front.
"""
from datetime import timedelta

from models.clinica.HorarioAtencion import HorarioAtencion
from models.clinica.EsquemaVacunacion import EsquemaVacunacion
from models.clinica.Tarifario import Tarifario


def persona(p):
    return {"dni": p.dni, "nombre": p.nombre, "apellido": p.apellido, "nombre_completo": p.nombre_completo(),
            "telefono": p.telefono, "email": p.email}


def cliente(c):
    return {**persona(c), "cantidad_mascotas": c.cantidad_mascotas()}


def veterinario(v):
    return {**persona(v), "matricula": v.matricula, "especialidad": v.especialidad, "clinica": v.clinica.nombre,
            "turno_laboral": v.turno_laboral, "horario": HorarioAtencion.texto(v.turno_laboral)}


def mascota(m):
    return {
        "id_mascota": m.id_mascota, "nombre": m.nombre, "especie": m.especie, "raza": m.raza,
        "fecha_nacimiento": m.fecha_nacimiento, "peso": m.peso, "activa": m.activa,
        "responsable": m.responsable.nombre_completo(), "dni_responsable": m.responsable.dni,
    }


def mascota_detalle(m):
    """Mascota con vacunas, vacunas pendientes e historia clínica (para el cliente)."""
    return {
        **mascota(m),
        "vacunas": [{"nombre": v.nombre, "fecha": v.fecha_aplicacion,
                     "vence": v.fecha_aplicacion + timedelta(days=EsquemaVacunacion.VIGENCIA_DIAS)}
                    for v in sorted(m.vacunas_aplicadas, key=lambda v: v.fecha_aplicacion, reverse=True)],
        "vacunas_pendientes": m.vacunas_pendientes(),
        "historia_clinica": [consulta(c) for c in m.historia_clinica()],
    }


def turno(t):
    return {
        "id_turno": t.numero, "tipo": t.tipo, "inicio": t.inicio, "fin": t.fin, "duracion_minutos": t.duracion_minutos,
        "mascota": t.mascota.nombre, "especie": t.mascota.especie, "responsable": t.mascota.responsable.nombre_completo(),
        "id_mascota": t.mascota.id_mascota, "veterinario": t.veterinario.nombre_completo(),
        "clinica": t.veterinario.clinica.nombre, "precio": Tarifario.precio_atencion(t.tipo),
        "motivo": t.motivo, "cancelado": t.cancelado, "atendido": t.atendido,
        "id_consulta": t.consulta.numero if t.consulta else None,
    }


def resultado(r):
    if r is None:
        return None
    return {"id_resultado": r.numero, "fecha": r.fecha_emision, "informe": r.informe,
            "bioquimico": r.bioquimico.nombre_completo()}


def muestra(m):
    orden = m.orden_derivacion
    return {
        "codigo": m.codigo_muestra, "tipo": m.tipo_muestra, "fecha_extraccion": m.fecha_extraccion,
        "estado": m.estado_actual.nombre(), "id_orden": orden.numero, "tipo_estudio": orden.tipo_estudio,
        "mascota": orden.consulta.mascota.nombre, "clinica": orden.clinica.nombre, "id_clinica": orden.clinica.id_clinica,
        "id_remito": m.remito.numero if m.remito else None,
        "reemplazada_por": m.reemplazada_por.codigo_muestra if m.reemplazada_por else None,
        "reextraccion_de": m.muestra_original.codigo_muestra if m.muestra_original else None,
        "motivo_rechazo": m.motivo_rechazo(),
        "resultado": resultado(m.resultado),
    }


def orden(o):
    return {"id_orden": o.numero, "fecha": o.fecha_emision, "tipo_estudio": o.tipo_estudio,
            "laboratorio": o.laboratorio.nombre, "muestras": [muestra(m) for m in o.muestras]}


def consulta(c):
    return {
        "id_consulta": c.numero, "fecha_hora": c.fecha_hora, "tipo_atencion": c.tipo_atencion,
        "id_turno": c.turno.numero if c.turno else None,
        "mascota": c.mascota.nombre, "id_mascota": c.mascota.id_mascota, "responsable": c.mascota.responsable.nombre_completo(),
        "veterinario": c.veterinario.nombre_completo(), "clinica": c.clinica.nombre, "motivo": c.motivo,
        "costo": c.costo, "diagnostico": c.diagnostico, "tratamiento": c.tratamiento,
        "vacunas_pendientes": c.vacunas_pendientes_detectadas, "ordenes": [orden(o) for o in c.ordenes_derivacion],
    }


def remito(r):
    p = r.precinto
    return {
        "id_remito": r.numero, "fecha_emision": r.fecha_emision, "estado": r.estado_actual.nombre(),
        "clinica": r.clinica.nombre, "laboratorio": r.laboratorio.nombre, "conservadora": r.conservadora.numero,
        "conservadora_temperatura": r.conservadora.temperatura_objetivo,
        "transportista": r.transportista, "fecha_despacho": r.fecha_despacho, "fecha_recepcion": r.fecha_recepcion,
        "precinto": {"codigo": p.codigo, "inspeccionado": p.inspeccionado, "intacto": p.esta_intacto,
                     "observaciones": p.observaciones_inspeccion},
        "muestras": [{"codigo": m.codigo_muestra, "tipo": m.tipo_muestra, "estado": m.estado_actual.nombre(),
                      "motivo_rechazo": m.motivo_rechazo()} for m in r.muestras],
        "con_observaciones": r.recibido_con_observaciones(),
        "eventos": [{"fecha_hora": e.fecha_hora, "ubicacion": e.ubicacion, "novedad": e.novedad,
                     "observacion": e.observacion, "tiene_novedad": e.tiene_novedad()} for e in r.eventos],
        "novedades": [f"{e.novedad}{' - ' + e.observacion if e.observacion else ''} ({e.ubicacion})"
                      for e in r.novedades_del_traslado()],
    }


def comprobante(c):
    return {
        "id_comprobante": c.numero, "fecha": c.fecha_emision, "clinica": c.consulta.clinica.nombre,
        "cliente": c.consulta.mascota.responsable.nombre_completo(), "mascota": c.consulta.mascota.nombre,
        "veterinario": c.consulta.veterinario.nombre_completo(),
        "items": [{"descripcion": i.descripcion, "importe": i.importe} for i in c.items], "total": c.total(),
    }
