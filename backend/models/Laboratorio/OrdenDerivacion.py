class OrdenDerivacion:
    """
    Orden emitida en una consulta para derivar muestras al laboratorio central.
    tipo_estudio es el ANÁLISIS que se pide (ej: Hemograma); el material que se
    extrae para hacerlo es el tipo de cada MuestraBiologica (ej: Sangre con EDTA).
    """

    ESTUDIOS = (
        "Hemograma", "Bioquímica sanguínea", "Panel infeccioso", "Urianálisis", "Urocultivo",
        "Coproparasitológico", "Citología", "Histopatología", "Cultivo y antibiograma",
    )

    def __init__(self, numero, fecha_emision, consulta, tipo_estudio, laboratorio):
        if tipo_estudio not in self.ESTUDIOS:
            raise ValueError(f"Estudio inválido: {tipo_estudio}.")
        self.numero = numero
        self.fecha_emision = fecha_emision
        self.consulta = consulta
        self.tipo_estudio = tipo_estudio
        self.laboratorio = laboratorio
        self.muestras = []

    @property
    def clinica(self):
        return self.consulta.clinica

    @property
    def veterinario(self):
        return self.consulta.veterinario

    def agregar_muestra(self, muestra):
        if muestra.orden_derivacion is not self:
            raise ValueError(f"La muestra {muestra.codigo_muestra} pertenece a otra orden de derivación.")
        if muestra not in self.muestras:
            self.muestras.append(muestra)

    def muestras_vigentes(self):
        """Muestras que siguen contando para la orden (excluye las rechazadas que ya se reemplazaron)."""
        return [m for m in self.muestras if m.reemplazada_por is None]

    def cantidad_muestras(self):
        return len(self.muestras_vigentes())

    def todas_muestras_analizadas(self):
        """True si la orden tiene muestras y todas las vigentes están analizadas."""
        vigentes = self.muestras_vigentes()
        return len(vigentes) > 0 and all(m.esta_analizada() for m in vigentes)

    def __str__(self):
        return (
            f"Orden #{self.numero} - Estudio: {self.tipo_estudio} | "
            f"{self.clinica.nombre} -> {self.laboratorio.nombre} | Paciente: {self.consulta.mascota.nombre} | "
            f"Muestras: {self.cantidad_muestras()}"
        )
