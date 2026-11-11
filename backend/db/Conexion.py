import sqlite3
from contextlib import contextmanager
from pathlib import Path

CARPETA_DB = Path(__file__).parent
RUTA_POR_DEFECTO = CARPETA_DB.parent / "veterinaria.db"

# =====================================================================
# PATRÓN DE DISEÑO: SINGLETON
#
# Toda la aplicación comparte una única conexión a la base de datos.
# Conexion() siempre devuelve la misma instancia; la primera vez abre el
# archivo, activa las claves foráneas y crea las tablas si no existen.
# =====================================================================


class Conexion:
    _instancia = None

    def __new__(cls, ruta=RUTA_POR_DEFECTO):
        if cls._instancia is None:
            instancia = super().__new__(cls)
            instancia._abrir(ruta)
            cls._instancia = instancia
        return cls._instancia

    def _abrir(self, ruta):
        self.ruta = Path(ruta)
        # check_same_thread=False: el servidor web puede atender pedidos desde otro hilo
        self._conexion = sqlite3.connect(self.ruta, check_same_thread=False)
        self._conexion.row_factory = sqlite3.Row          # Permite leer columnas por nombre: fila["nombre"]
        self._conexion.execute("PRAGMA foreign_keys = ON")  # SQLite no controla FKs si no se activa
        self._profundidad = 0
        self._crear_tablas()

    def _crear_tablas(self):
        self.ejecutar_script("schema.sql")
        self._migrar()
        self.ejecutar_script("datos_iniciales.sql")

    def _migrar(self):
        """
        Adapta una base creada con una versión anterior del sistema, sin perder sus datos.
        (CREATE TABLE IF NOT EXISTS no modifica tablas que ya existen.)
        """
        columnas = [f["name"] for f in self.consultar("PRAGMA table_info(vacuna_aplicada)")]
        if "lote" in columnas:  # Se dejó de registrar el lote de las vacunas
            self._conexion.execute("ALTER TABLE vacuna_aplicada DROP COLUMN lote")
            self._conexion.commit()

        columnas = [f["name"] for f in self.consultar("PRAGMA table_info(evento_traslado)")]
        if "temperatura" in columnas:  # Los eventos pasan a registrar una novedad en vez de la temperatura
            self._conexion.execute("ALTER TABLE evento_traslado ADD COLUMN novedad TEXT NOT NULL DEFAULT 'Sin novedad'")
            self._conexion.execute(
                "UPDATE evento_traslado SET novedad = 'Cadena de frío interrumpida' "
                "WHERE temperatura IS NOT NULL AND (temperatura < 2 OR temperatura > 8)"
            )
            self._conexion.execute("ALTER TABLE evento_traslado DROP COLUMN temperatura")
            self._conexion.commit()

        columnas = [f["name"] for f in self.consultar("PRAGMA table_info(resultado_analisis)")]
        if "observaciones" in columnas:  # El resultado pasa a ser un informe en texto libre
            self._conexion.execute("ALTER TABLE resultado_analisis ADD COLUMN informe TEXT NOT NULL DEFAULT ''")
            self._conexion.execute("""
                UPDATE resultado_analisis SET informe = TRIM(
                    COALESCE((SELECT GROUP_CONCAT(v.parametro || ': ' || v.valor, char(10))
                              FROM valor_resultado v WHERE v.id_resultado = resultado_analisis.id_resultado), '')
                    || char(10) || COALESCE(observaciones, ''), char(10) || ' ')
            """)
            self._conexion.execute("ALTER TABLE resultado_analisis DROP COLUMN observaciones")
            self._conexion.execute("DROP TABLE IF EXISTS valor_resultado")
            self._conexion.commit()

    def ejecutar_script(self, archivo):
        """Ejecuta un archivo .sql de la carpeta db/."""
        script = (CARPETA_DB / archivo).read_text(encoding="utf-8")
        self._conexion.executescript(script)
        self._conexion.commit()

    def ejecutar(self, sql, parametros=()):
        return self._conexion.execute(sql, parametros)

    def consultar(self, sql, parametros=()):
        return self._conexion.execute(sql, parametros).fetchall()

    @contextmanager
    def transaccion(self):
        """
        Agrupa varias operaciones: si todas salen bien se confirman (commit);
        si alguna falla se deshacen todas (rollback). Admite anidamiento: solo
        la transacción más externa confirma.
        """
        self._profundidad += 1
        try:
            yield
            if self._profundidad == 1:
                self._conexion.commit()
        except Exception:
            if self._profundidad == 1:
                self._conexion.rollback()
            raise
        finally:
            self._profundidad -= 1

    @classmethod
    def cerrar(cls):
        if cls._instancia is not None:
            cls._instancia._conexion.close()
            cls._instancia = None
