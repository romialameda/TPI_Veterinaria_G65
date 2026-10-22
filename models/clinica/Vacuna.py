class Vacuna:
    def __init__(self, nombre, lote, fecha_aplicacion):
        self.nombre = nombre  
        self.lote = lote
        self.fecha_aplicacion = fecha_aplicacion

    def __str__(self):
        return f"Vacuna: {self.nombre} (Lote: {self.lote}, Fecha: {self.fecha_aplicacion})"