"""
Conversiones entre bases: decimal, binaria, octal y hexadecimal.
Algoritmos manuales: suma de potencias (X -> decimal) y
divisiones sucesivas (decimal -> X).
"""

DIGITOS = "0123456789ABCDEF"   # dígitos válidos (hasta base 16)

BASE_BIN, BASE_OCT, BASE_DEC, BASE_HEX = 2, 8, 10, 16


def _validar_base(base: int):
    if not 2 <= base <= 16:
        raise ValueError("La base debe estar entre 2 y 16.")


def validar_numero(numero_str: str, base: int) -> str:
    """Devuelve el número en mayúsculas (con su signo) o lanza ValueError."""
    _validar_base(base)

    numero = numero_str.upper().strip()
    if not numero:
        raise ValueError("El número no puede estar vacío.")

    signo = ""
    if numero[0] in "+-":                      # signo opcional
        signo, numero = numero[0], numero[1:]
        if not numero:
            raise ValueError("Número inválido.")

    validos = DIGITOS[:base]                   # p.ej. base 2 -> "01"
    for c in numero:
        if c not in validos:
            raise ValueError(
                f"El dígito '{c}' no es válido en base {base}. "
                f"Dígitos permitidos: {validos}"
            )
    return signo + numero


def a_decimal(numero_str: str, base: int) -> int:
    """Cualquier base -> decimal, sumando dígito × base^posición."""
    numero = validar_numero(numero_str, base)
    signo = -1 if numero[0] == "-" else 1
    numero = numero.lstrip("+-")

    decimal = 0
    for i, c in enumerate(reversed(numero)):   # i = posición desde la derecha
        decimal += DIGITOS.index(c) * base ** i
    return signo * decimal


def desde_decimal(decimal: int, base: int) -> str:
    """Decimal -> cualquier base, con divisiones sucesivas."""
    _validar_base(base)
    if decimal == 0:
        return "0"

    signo = "-" if decimal < 0 else ""
    decimal = abs(decimal)

    resultado = ""
    while decimal > 0:
        resultado = DIGITOS[decimal % base] + resultado   # residuo, se antepone
        decimal //= base
    return signo + resultado


def convertir(numero_str: str, base_origen: int, base_destino: int) -> str:
    """Base X -> base Y, usando el decimal como puente."""
    return desde_decimal(a_decimal(numero_str, base_origen), base_destino)
