"""
Módulo de conversiones numéricas entre bases: decimal, binaria, octal y hexadecimal.
Se implementan los algoritmos manualmente (divisiones sucesivas y suma de potencias).
"""

DIGITOS = "0123456789ABCDEF"   # dígitos válidos (hasta base 16)

BASE_BIN = 2
BASE_OCT = 8
BASE_DEC = 10
BASE_HEX = 16


# ----------------------------------------------------------------------
# Validación
# ----------------------------------------------------------------------
def validar_numero(numero_str: str, base: int) -> str:
    """
    Verifica que la cadena solo contenga dígitos válidos para la base.
    Devuelve la cadena en mayúsculas y sin espacios.
    Lanza ValueError si es inválida.
    """
    if base < 2 or base > 16:
        raise ValueError("La base debe estar entre 2 y 16.")

    numero = numero_str.upper().strip()
    if not numero:
        raise ValueError("El número no puede estar vacío.")

    # Signo opcional
    signo = ""
    if numero[0] in "+-":
        signo, numero = numero[0], numero[1:]
        if not numero:
            raise ValueError("Número inválido.")

    validos = DIGITOS[:base]           # p.ej. base 2 -> "01"
    for c in numero:
        if c not in validos:
            raise ValueError(
                f"El dígito '{c}' no es válido en base {base}. "
                f"Dígitos permitidos: {validos}"
            )
    return signo + numero


# ----------------------------------------------------------------------
# Cualquier base  ->  Decimal  (suma de potencias)
# ----------------------------------------------------------------------
def a_decimal(numero_str: str, base: int) -> int:
    numero = validar_numero(numero_str, base)

    signo = -1 if numero.startswith("-") else 1
    numero = numero.lstrip("+-")

    decimal = 0
    for i, c in enumerate(reversed(numero)):
        decimal += DIGITOS.index(c) * (base ** i)

    return signo * decimal


# ----------------------------------------------------------------------
# Decimal  ->  Cualquier base  (divisiones sucesivas)
# ----------------------------------------------------------------------
def desde_decimal(decimal: int, base: int) -> str:
    if base < 2 or base > 16:
        raise ValueError("La base debe estar entre 2 y 16.")
    if decimal == 0:
        return "0"

    signo = "-" if decimal < 0 else ""
    decimal = abs(decimal)

    resultado = ""
    while decimal > 0:
        residuo = decimal % base
        resultado = DIGITOS[residuo] + resultado   # se antepone
        decimal //= base

    return signo + resultado


# ----------------------------------------------------------------------
# Conversión general (base X -> base Y, pasando por decimal)
# ----------------------------------------------------------------------
def convertir(numero_str: str, base_origen: int, base_destino: int) -> str:
    return desde_decimal(a_decimal(numero_str, base_origen), base_destino)
