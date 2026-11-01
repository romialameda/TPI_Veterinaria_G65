"""Conversión entre fechas de Python y el texto ISO que se guarda en SQLite."""
from datetime import date, datetime


def a_texto(valor):
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.isoformat(sep=" ", timespec="seconds")
    return valor.isoformat()


def a_fecha_hora(texto):
    return datetime.fromisoformat(texto) if texto else None


def a_fecha(texto):
    return date.fromisoformat(texto) if texto else None
