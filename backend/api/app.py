"""
API web del sistema. Recibe los pedidos del front (React), llama a los servicios y devuelve JSON.
No tiene lógica de negocio: todo lo resuelven los servicios y el modelo.

Ejecutar desde la carpeta del proyecto:   uvicorn api.app:app --reload
Documentación y pruebas en el navegador:  http://localhost:8000/docs

Los endpoints son "async def" para que FastAPI los atienda de a uno por vez
y la conexión SQLite compartida no se use desde dos lugares al mismo tiempo.
"""
from datetime import datetime, date

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api import convertir
from db.Conexion import Conexion
from db.Repositorio import Repositorio
from dao.UsuarioDAO import UsuarioDAO
from db.datos_demo import cargar_datos_demo
from services.ServicioClientes import ServicioClientes
from services.ServicioAtencion import ServicioAtencion
from services.ServicioLaboratorio import ServicioLaboratorio
from services.ServicioUsuarios import ServicioUsuarios
from Reports.GeneradorReportes import GeneradorReportes
from models.clinica.EsquemaVacunacion import EsquemaVacunacion
from models.clinica.Turno import Turno
from models.Laboratorio.OrdenDerivacion import OrdenDerivacion
from models.Laboratorio.MuestraBiologica import MuestraBiologica

ARANCEL_LAB_POR_MUESTRA = 4500.0

# --- Inicio: abre la base, la completa con datos de ejemplo si está vacía y carga los objetos ---
conexion = Conexion()
base_nueva = not UsuarioDAO(conexion).hay_usuarios()
if base_nueva:
    conexion.ejecutar_script("datos_ejemplo.sql")  # Sedes, profesionales y usuarios
repo = Repositorio(conexion).cargar()

clientes = ServicioClientes(repo)
atencion = ServicioAtencion(repo)
laboratorio = ServicioLaboratorio(repo)
usuarios = ServicioUsuarios(repo)

if base_nueva:
    cargar_datos_demo(repo, clientes, atencion, laboratorio, usuarios)  # Turnos, consultas, muestras...

app = FastAPI(title="Veterinaria - Red de Clínicas y Laboratorio")


@app.exception_handler(ValueError)
async def error_de_negocio(request: Request, error: ValueError):
    """Las validaciones del modelo lanzan ValueError: se devuelven al front como error 400 con el mensaje."""
    return JSONResponse(status_code=400, content={"detail": str(error)})


def buscar(diccionario, clave, que):
    if clave not in diccionario:
        raise ValueError(f"No existe {que} {clave}.")
    return diccionario[clave]


# =====================================================================
# LOGIN
# =====================================================================
class DatosLogin(BaseModel):
    usuario: str
    contrasena: str


@app.post("/login")
async def login(datos: DatosLogin):
    u = usuarios.login(datos.usuario, datos.contrasena)
    respuesta = {"usuario": u.nombre_usuario, "rol": u.rol, "nombre": "Recepción"}
    if u.persona is not None:
        respuesta["nombre"] = u.persona.nombre_completo()
        respuesta["matricula"] = getattr(u.persona, "matricula", None)
        respuesta["dni"] = u.persona.dni
    return respuesta


# =====================================================================
# DATOS GENERALES (para completar listas desplegables)
# =====================================================================
@app.get("/clinicas")
async def listar_clinicas():
    return [{"id_clinica": c.id_clinica, "nombre": c.nombre} for c in repo.clinicas.values()]


@app.get("/laboratorios")
async def listar_laboratorios():
    return [{"id_laboratorio": l.id_laboratorio, "nombre": l.nombre} for l in repo.laboratorios.values()]


@app.get("/veterinarios")
async def listar_veterinarios():
    orden = sorted(repo.veterinarios.values(), key=lambda v: (v.clinica.nombre, v.turno_laboral != "Mañana"))
    return [convertir.veterinario(v) for v in orden]


@app.get("/especies")
async def listar_especies():
    return EsquemaVacunacion.especies()


@app.get("/vacunas")
async def catalogo_vacunas(especie: str):
    obligatorias = EsquemaVacunacion.obligatorias_para(especie)
    return [{"nombre": n, "obligatoria": n in obligatorias} for n in EsquemaVacunacion.disponibles_para(especie)]


@app.get("/estudios")
async def listar_estudios():
    return list(OrdenDerivacion.ESTUDIOS)


@app.get("/tipos-muestra")
async def listar_tipos_muestra():
    return list(MuestraBiologica.TIPOS_MUESTRA)


@app.get("/conservadoras")
async def listar_conservadoras_disponibles():
    return [{"numero": c.numero, "capacidad_maxima": c.capacidad_maxima, "temperatura": c.temperatura_objetivo}
            for c in laboratorio.conservadoras_disponibles()]


# =====================================================================
# SECRETARIO: clientes y mascotas
# =====================================================================
class NuevoCliente(BaseModel):
    dni: str
    nombre: str
    apellido: str
    telefono: str
    email: str = ""
    contrasena: str  # Contraseña para que el cliente entre al sistema (su usuario es el DNI)


@app.get("/clientes")
async def listar_clientes():
    return [convertir.cliente(c) for c in clientes.listar_clientes()]


@app.post("/clientes")
async def alta_cliente(datos: NuevoCliente):
    if datos.dni in repo.usuarios:
        raise ValueError(f"Ya existe el usuario {datos.dni}.")
    cliente = clientes.alta_cliente(datos.dni, datos.nombre, datos.apellido, datos.telefono, datos.email)
    usuarios.crear_usuario(datos.dni, datos.contrasena, "Cliente", cliente)
    return convertir.cliente(cliente)


class NuevaMascota(BaseModel):
    nombre: str
    especie: str
    raza: str = ""
    fecha_nacimiento: date | None = None
    peso: float
    dni_responsable: str


@app.get("/mascotas")
async def listar_mascotas():
    return [convertir.mascota(m) for m in repo.mascotas.values() if m.activa]


@app.post("/mascotas")
async def alta_mascota(datos: NuevaMascota):
    m = clientes.alta_mascota(datos.nombre, datos.especie, datos.raza, datos.fecha_nacimiento,
                              datos.peso, datos.dni_responsable)
    return convertir.mascota(m)


class NuevaVacuna(BaseModel):
    nombre: str
    fecha_aplicacion: date


@app.get("/mascotas/{id_mascota}/historia")
async def historia_clinica(id_mascota: int):
    """Historia clínica completa: datos, vacunas y todas sus consultas (con cualquier veterinario)."""
    return convertir.mascota_detalle(clientes.buscar_mascota(id_mascota))


@app.post("/mascotas/{id_mascota}/vacunas")
async def registrar_vacuna(id_mascota: int, datos: NuevaVacuna):
    clientes.registrar_vacuna(id_mascota, datos.nombre, datos.fecha_aplicacion)
    return convertir.mascota_detalle(clientes.buscar_mascota(id_mascota))


# =====================================================================
# SECRETARIO: agenda de turnos
# =====================================================================
class NuevoTurno(BaseModel):
    inicio: datetime
    tipo: str          # "Consulta" (45 min) o "Control" (30 min)
    id_mascota: int
    matricula_veterinario: str
    motivo: str


@app.get("/turnos/tipos")
async def tipos_de_turno():
    return [{"tipo": tipo, "duracion_minutos": minutos} for tipo, minutos in Turno.DURACIONES.items()]


@app.get("/turnos/horarios")
async def horarios_disponibles(fecha: date, matricula_veterinario: str, tipo: str):
    vet = atencion.buscar_veterinario(matricula_veterinario)
    return [h.strftime("%H:%M") for h in atencion.horarios_disponibles(vet, fecha, tipo)]


@app.get("/turnos")
async def listar_turnos(fecha: date):
    turnos = [t for t in repo.turnos if t.inicio.date() == fecha]
    return [convertir.turno(t) for t in sorted(turnos, key=lambda t: t.inicio)]


@app.post("/turnos")
async def agendar_turno(datos: NuevoTurno):
    t = atencion.agendar_turno(
        datos.inicio, datos.tipo, clientes.buscar_mascota(datos.id_mascota),
        atencion.buscar_veterinario(datos.matricula_veterinario), datos.motivo,
    )
    return convertir.turno(t)


@app.post("/turnos/{id_turno}/cancelar")
async def cancelar_turno(id_turno: int):
    turno = next((t for t in repo.turnos if t.numero == id_turno), None)
    if turno is None:
        raise ValueError(f"No existe el turno {id_turno}.")
    atencion.cancelar_turno(turno)
    return convertir.turno(turno)


# =====================================================================
# SECRETARIO: logística (remitos) y comprobantes
# =====================================================================
@app.get("/muestras")
async def listar_muestras(estado: str | None = None):
    return [convertir.muestra(m) for m in repo.muestras.values()
            if estado is None or m.estado_actual.nombre() == estado]


class NuevoRemito(BaseModel):
    id_clinica: int
    id_laboratorio: int
    numero_conservadora: int
    codigos_muestras: list[str]


@app.get("/remitos")
async def listar_remitos(estado: str | None = None):
    return [convertir.remito(r) for r in sorted(repo.remitos.values(), key=lambda r: r.numero, reverse=True)
            if estado is None or r.estado_actual.nombre() == estado]


@app.post("/remitos")
async def armar_remito(datos: NuevoRemito):
    muestras = [buscar(repo.muestras, codigo, "la muestra") for codigo in datos.codigos_muestras]
    r = laboratorio.empaquetar(
        datetime.now(), buscar(repo.clinicas, datos.id_clinica, "la clínica"),
        buscar(repo.laboratorios, datos.id_laboratorio, "el laboratorio"),
        buscar(repo.conservadoras, datos.numero_conservadora, "la conservadora"), muestras,
    )
    return convertir.remito(r)


class Despacho(BaseModel):
    transportista: str


@app.post("/remitos/{id_remito}/despachar")
async def despachar_remito(id_remito: int, datos: Despacho):
    r = buscar(repo.remitos, id_remito, "el remito")
    laboratorio.despachar(r, datetime.now(), datos.transportista)
    return convertir.remito(r)


class Evento(BaseModel):
    ubicacion: str
    descripcion: str
    temperatura: float | None = None


@app.post("/remitos/{id_remito}/eventos")
async def registrar_evento(id_remito: int, datos: Evento):
    r = buscar(repo.remitos, id_remito, "el remito")
    laboratorio.registrar_evento_traslado(r, datetime.now(), datos.ubicacion, datos.descripcion, datos.temperatura)
    return convertir.remito(r)


@app.get("/consultas")
async def listar_consultas():
    return [convertir.consulta(c) for c in sorted(repo.consultas.values(), key=lambda c: c.fecha_hora, reverse=True)]


@app.post("/consultas/{id_consulta}/comprobante")
async def emitir_comprobante(id_consulta: int):
    consulta = buscar(repo.consultas, id_consulta, "la consulta")
    return convertir.comprobante(atencion.emitir_comprobante(datetime.now(), consulta, ARANCEL_LAB_POR_MUESTRA))


# =====================================================================
# SECRETARIO: reportes
# =====================================================================
@app.get("/reportes")
async def reportes():
    g = GeneradorReportes(list(repo.consultas.values()), list(repo.remitos.values()),
                          list(repo.muestras.values()), list(repo.mascotas.values()))
    return {
        "atenciones": g.reporte_atenciones_y_derivaciones(),
        "rechazadas": g.reporte_muestras_rechazadas(),
        "vacunas": g.reporte_tratamientos_y_vacunas(),
        "facturacion": g.reporte_facturacion_por_clinica(ARANCEL_LAB_POR_MUESTRA),
        "tiempos": g.reporte_tiempos(),
    }


# =====================================================================
# VETERINARIO
# =====================================================================
@app.get("/veterinarios/{matricula}/turnos")
async def agenda_veterinario(matricula: str, fecha: date):
    vet = atencion.buscar_veterinario(matricula)
    return [convertir.turno(t) for t in vet.agenda_del_dia(fecha)]


@app.get("/veterinarios/{matricula}/consultas")
async def consultas_veterinario(matricula: str):
    vet = atencion.buscar_veterinario(matricula)
    return [convertir.consulta(c) for c in sorted(vet.consultas, key=lambda c: c.fecha_hora, reverse=True)]


class AtencionDeTurno(BaseModel):
    costo: float


@app.post("/turnos/{id_turno}/atender")
async def atender_turno(id_turno: int, datos: AtencionDeTurno):
    """La mascota, el tipo y el motivo salen del turno: no se pueden cambiar."""
    turno = next((t for t in repo.turnos if t.numero == id_turno), None)
    if turno is None:
        raise ValueError(f"No existe el turno {id_turno}.")
    return convertir.consulta(atencion.atender_turno(turno, datetime.now(), datos.costo))


class NuevaUrgencia(BaseModel):
    id_mascota: int
    matricula_veterinario: str
    motivo: str
    costo: float


@app.post("/consultas/urgencia")
async def registrar_urgencia(datos: NuevaUrgencia):
    c = atencion.registrar_urgencia(
        datetime.now(), clientes.buscar_mascota(datos.id_mascota),
        atencion.buscar_veterinario(datos.matricula_veterinario), datos.motivo, datos.costo,
    )
    return convertir.consulta(c)


class Diagnostico(BaseModel):
    diagnostico: str
    tratamiento: str


@app.put("/consultas/{id_consulta}/diagnostico")
async def registrar_diagnostico(id_consulta: int, datos: Diagnostico):
    c = buscar(repo.consultas, id_consulta, "la consulta")
    atencion.registrar_diagnostico(c, datos.diagnostico, datos.tratamiento)
    return convertir.consulta(c)


class NuevaOrden(BaseModel):
    tipo_estudio: str
    id_laboratorio: int


@app.post("/consultas/{id_consulta}/ordenes")
async def emitir_orden(id_consulta: int, datos: NuevaOrden):
    c = buscar(repo.consultas, id_consulta, "la consulta")
    atencion.emitir_orden_derivacion(datetime.now(), c, datos.tipo_estudio,
                                     buscar(repo.laboratorios, datos.id_laboratorio, "el laboratorio"))
    return convertir.consulta(c)


class NuevaMuestra(BaseModel):
    tipo_muestra: str


@app.post("/ordenes/{id_orden}/muestras")
async def registrar_extraccion(id_orden: int, datos: NuevaMuestra):
    """El código de la muestra lo genera el sistema y se devuelve para etiquetar el tubo."""
    o = buscar(repo.ordenes, id_orden, "la orden")
    m = laboratorio.registrar_extraccion(datos.tipo_muestra, datetime.now(), o)
    return {"codigo": m.codigo_muestra, "consulta": convertir.consulta(o.consulta)}


@app.post("/muestras/{codigo}/reextraccion")
async def reextraer_muestra(codigo: str):
    m = buscar(repo.muestras, codigo, "la muestra")
    nueva = laboratorio.solicitar_reextraccion(m, datetime.now())
    return {"codigo": nueva.codigo_muestra, "consulta": convertir.consulta(m.orden_derivacion.consulta)}


# =====================================================================
# BIOQUÍMICO
# =====================================================================
class Recepcion(BaseModel):
    matricula_bioquimico: str
    precinto_intacto: bool
    observaciones: str = ""


@app.post("/remitos/{id_remito}/recibir")
async def recibir_remito(id_remito: int, datos: Recepcion):
    r = buscar(repo.remitos, id_remito, "el remito")
    bioq = buscar(repo.bioquimicos, datos.matricula_bioquimico, "el bioquímico")
    laboratorio.recibir_remito(r, datetime.now(), datos.precinto_intacto, bioq, datos.observaciones)
    return convertir.remito(r)


class NuevoResultado(BaseModel):
    matricula_bioquimico: str
    valores: dict[str, str]
    observaciones: str = ""


@app.post("/muestras/{codigo}/resultado")
async def cargar_resultado(codigo: str, datos: NuevoResultado):
    m = buscar(repo.muestras, codigo, "la muestra")
    bioq = buscar(repo.bioquimicos, datos.matricula_bioquimico, "el bioquímico")
    laboratorio.registrar_resultado(datetime.now(), m, datos.valores, datos.observaciones, bioq)
    return convertir.muestra(m)


# =====================================================================
# CLIENTE (solo lectura)
# =====================================================================
@app.get("/clientes/{dni}/mascotas")
async def mascotas_del_cliente(dni: str):
    cliente = clientes.buscar_cliente(dni)
    return [convertir.mascota_detalle(m) for m in cliente.mascotas_activas()]
