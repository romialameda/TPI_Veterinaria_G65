class Mascota:
    def __init__(self, id_mascota, nombre, especie, raza, fecha_nacimiento, peso, responsable):
        # Validación obligatoria: toda mascota debe tener responsable
        if responsable is None:
            raise ValueError("Toda mascota debe tener un responsable asociado.")

        self.id_mascota = id_mascota
        self.nombre = nombre
        self.especie = especie  
        self.raza = raza
        self.fecha_nacimiento = fecha_nacimiento
        self.peso = peso
        self.responsable = responsable
        self.vacunas_aplicadas = []
        self.consultas = []

        # Vinculación automática con el cliente responsable
        self.responsable.agregar_mascota(self)

    def registrar_vacuna(self, vacuna):
        self.vacunas_aplicadas.append(vacuna)

    def registrar_consulta(self, consulta):
        self.consultas.append(consulta)

    def tiene_vacuna(self, nombre_vacuna):
        for v in self.vacunas_aplicadas:
            if v.nombre.lower() == nombre_vacuna.lower():
                return True
        return False

    def vacunas_pendientes(self, vacunas_obligatorias):
        """Devuelve la lista de vacunas que le faltan según una lista requerida."""
        faltantes = []
        for v_req in vacunas_obligatorias:
            if not self.tiene_vacuna(v_req):
                faltantes.append(v_req)
        return faltantes

    def __str__(self):
        return (
            f"Mascota #{self.id_mascota}: {self.nombre} ({self.especie} - {self.raza}) "
            f"- Dueño: {self.responsable.nombre_completo()} - Peso: {self.peso}kg"
        )