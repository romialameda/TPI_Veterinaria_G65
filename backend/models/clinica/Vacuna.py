class Vacuna:
    def __init__(self, nombre, fecha_aplicacion):
        self.id_vacuna = None  # Lo asigna la base de datos
        self.nombre = nombre
        self.fecha_aplicacion = fecha_aplicacion

    def __str__(self):
        return f"Vacuna: {self.nombre} (aplicada el {self.fecha_aplicacion.strftime('%d/%m/%Y')})"
