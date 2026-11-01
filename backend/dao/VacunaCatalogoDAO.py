class VacunaCatalogoDAO:
    def __init__(self, conexion):
        self.db = conexion

    def listar_por_especie(self):
        """Devuelve {especie: {nombre_vacuna: es_obligatoria}}."""
        catalogo = {}
        for f in self.db.consultar("SELECT * FROM vacuna_catalogo ORDER BY especie, obligatoria DESC, nombre_vacuna"):
            catalogo.setdefault(f["especie"], {})[f["nombre_vacuna"]] = bool(f["obligatoria"])
        return catalogo
