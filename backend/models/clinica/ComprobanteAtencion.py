class ItemComprobante:
    def __init__(self, descripcion, importe):
        self.id_item = None
        self.descripcion = descripcion
        self.importe = importe


class ComprobanteAtencion:
    """Comprobante que se entrega al cliente por una atención clínica y sus análisis."""

    def __init__(self, numero, fecha_emision, consulta):
        self.numero = numero
        self.fecha_emision = fecha_emision
        self.consulta = consulta
        self.items = []

    def agregar_item(self, descripcion, importe):
        if importe < 0:
            raise ValueError("El importe de un ítem no puede ser negativo.")
        self.items.append(ItemComprobante(descripcion, importe))

    def total(self):
        return sum(i.importe for i in self.items)

    def __str__(self):
        c = self.consulta
        lineas = [
            "-" * 60,
            f"COMPROBANTE DE ATENCIÓN #{self.numero} - {self.fecha_emision.strftime('%d/%m/%Y %H:%M')}",
            f"{c.clinica.nombre} - {c.clinica.direccion}",
            f"Cliente : {c.mascota.responsable.nombre_completo()} (DNI {c.mascota.responsable.dni})",
            f"Paciente: {c.mascota.nombre} ({c.mascota.especie})",
            f"Atendió : {c.veterinario.nombre_completo()} (MP {c.veterinario.matricula})",
            "-" * 60,
        ]
        for item in self.items:
            lineas.append(f"{item.descripcion:<45} ${item.importe:>12,.2f}")
        lineas.append("-" * 60)
        lineas.append(f"{'TOTAL':<45} ${self.total():>12,.2f}")
        lineas.append("-" * 60)
        return "\n".join(lineas)
