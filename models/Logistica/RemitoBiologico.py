class RemitoBiologico:
    def __init__(self, numero, fecha_emision, clinica, laboratorio, conservadora, precinto):
        self.numero = numero
        self.fecha_emision = fecha_emision
        self.clinica = clinica
        self.laboratorio = laboratorio
        self.conservadora = conservadora
        self.precinto = precinto
        self.muestras = []
        self.fecha_recepcion = None

    def agregar_muestra(self, muestra):
        """Empaqueta una muestra validando la capacidad de la conservadora."""
        if len(self.muestras) >= self.conservadora.capacidad_maxima:
            raise ValueError(f"La conservadora #{self.conservadora.numero} superó su capacidad máxima.")

        # Dispara la transición de estado de la muestra a 'Empaquetada'
        muestra.empaquetar(self.conservadora)
        self.muestras.append(muestra)

    def despachar(self):
        """Pone todas las muestras del remito en tránsito hacia el laboratorio central."""
        if not self.muestras:
            raise ValueError("No se puede despachar un remito sin muestras.")
        for muestra in self.muestras:
            muestra.despachar()

    def recibir_en_laboratorio(self, fecha_recepcion):
        """
        Registra la recepción verificando el precinto sanitario.
        Si el precinto está roto, las muestras pasan automáticamente a Rechazadas.
        """
        self.fecha_recepcion = fecha_recepcion
        precinto_valido = self.precinto.es_valido()

        for muestra in self.muestras:
            muestra.recibir(precinto_valido)

    def cantidad_muestras(self):
        return len(self.muestras)

    def __str__(self):
        return (
            f"Remito #{self.numero} | Origen: {self.clinica} -> Destino: {self.laboratorio} | "
            f"Muestras: {self.cantidad_muestras()} | {self.precinto}"
        )