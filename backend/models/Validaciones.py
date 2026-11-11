"""
Validaciones básicas de datos de entrada. Cada función devuelve el valor limpio
(sin espacios de más) o lanza ValueError con un mensaje para mostrar al usuario.
"""
import re
from datetime import date


def texto_obligatorio(valor, campo, maximo=200):
    texto = (valor or "").strip()
    if not texto:
        raise ValueError(f"El campo '{campo}' es obligatorio.")
    if len(texto) > maximo:
        raise ValueError(f"El campo '{campo}' no puede superar los {maximo} caracteres.")
    return texto


def solo_letras(valor, campo):
    """Nombres y apellidos: letras (con tildes y ñ), espacios, apóstrofo y guion."""
    texto = texto_obligatorio(valor, campo, 60)
    if not re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+", texto):
        raise ValueError(f"El campo '{campo}' solo puede contener letras.")
    return texto


def dni(valor):
    texto = str(valor or "").strip()
    if not re.fullmatch(r"\d{7,8}", texto):
        raise ValueError("El DNI debe tener 7 u 8 números, sin puntos ni letras.")
    return texto


def telefono(valor):
    texto = texto_obligatorio(valor, "Teléfono", 20)
    if not re.fullmatch(r"\+?[\d -]{7,20}", texto) or sum(c.isdigit() for c in texto) < 7:
        raise ValueError("El teléfono solo puede tener números, espacios o guiones (mínimo 7 números).")
    return texto


def email(valor, obligatorio=False):
    texto = (valor or "").strip()
    if not texto and not obligatorio:
        return ""
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", texto):
        raise ValueError("El email no tiene un formato válido (ejemplo: nombre@mail.com).")
    return texto


def numero_en_rango(valor, campo, minimo, maximo):
    if valor is None or not minimo <= valor <= maximo:
        raise ValueError(f"El campo '{campo}' debe estar entre {minimo} y {maximo}.")
    return valor


def fecha_no_futura(valor, campo):
    if valor is not None and valor > date.today():
        raise ValueError(f"La {campo} no puede ser una fecha futura.")
    return valor
