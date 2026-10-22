class Conservadora:
    def __init__(self, numero, capacidad_maxima, temperatura_objetivo):
        self.numero = numero
        self.capacidad_maxima = capacidad_maxima  
        self.temperatura_objetivo = temperatura_objetivo 

    def __str__(self):
        return f"Conservadora #{self.numero} (Capacidad: {self.capacidad_maxima} muestras, Temp: {self.temperatura_objetivo})"