"""
Operaciones aritméticas con signo.
- El decimal sirve de puente entre bases.
- Los algoritmos en complemento a dos (C2) devuelven el proceso paso a paso.
"""

from conversiones import a_decimal, desde_decimal


# ----------------------------------------------------------------------
# Utilidades pequeñas
# ----------------------------------------------------------------------
def _mascara(bits: int) -> int:
    """Ej.: 8 bits -> 0b11111111. Sirve para 'recortar' a N bits."""
    return (1 << bits) - 1


def _invertir(bin_str: str) -> str:
    """Complemento a uno: cambia 0 por 1 y 1 por 0."""
    return "".join("1" if c == "0" else "0" for c in bin_str)


def _signo(n: int) -> str:
    return "+" if n >= 0 else "-"


# ----------------------------------------------------------------------
# Complemento a dos
# ----------------------------------------------------------------------
def c2(valor: int, bits: int) -> str:
    """Representación de 'valor' (con signo) en C2 de 'bits' bits."""
    rango = 1 << (bits - 1)
    if not -rango <= valor < rango:
        raise ValueError(
            f"El valor {valor} no cabe en {bits} bits "
            f"(rango C2: -{rango} a {rango - 1})."
        )
    return format(valor & _mascara(bits), f"0{bits}b")


def leer_c2(bin_str: str) -> int:
    """Interpreta una cadena binaria como número con signo en C2."""
    v = int(bin_str, 2)
    if bin_str[0] == "1":              # bit de signo encendido -> negativo
        v -= 1 << len(bin_str)
    return v


# ----------------------------------------------------------------------
# Suma en C2 (con detección de overflow)
# ----------------------------------------------------------------------
def suma_c2_pasos(a_bin: str, b_bin: str):
    bits = len(a_bin)
    res = format((int(a_bin, 2) + int(b_bin, 2)) & _mascara(bits), f"0{bits}b")

    # Overflow: dos signos iguales dan un signo distinto
    overflow = a_bin[0] == b_bin[0] and res[0] != a_bin[0]

    pasos = [
        f"  {a_bin}   ({leer_c2(a_bin):+d})",
        f"+ {b_bin}   ({leer_c2(b_bin):+d})",
        "  " + "-" * (bits + 8),
        f"  {res}   ({leer_c2(res):+d})",
    ]
    if overflow:
        pasos += ["", "⚠ OVERFLOW: el resultado no cabe en los bits indicados."]
    return res, pasos


# ----------------------------------------------------------------------
# Resta en C2:  a - b = a + (-b)
# ----------------------------------------------------------------------
def resta_c2_pasos(a_bin: str, b_bin: str):
    bits = len(a_bin)
    inv_b = _invertir(b_bin)
    neg_b = format((int(inv_b, 2) + 1) & _mascara(bits), f"0{bits}b")

    res, pasos_suma = suma_c2_pasos(a_bin, neg_b)
    encabezado = [
        "a - b   ==>   a + (-b)",
        f"-b = inv({b_bin}) + 1 = {inv_b} + 1 = {neg_b}",
        "",
    ]
    return res, encabezado + pasos_suma


# ----------------------------------------------------------------------
# Multiplicación: regla de signos + suma de productos parciales
# ----------------------------------------------------------------------
def multiplicar_c2_pasos(a_bin: str, b_bin: str):
    a, b = leer_c2(a_bin), leer_c2(b_bin)
    signo = "-" if (a < 0) != (b < 0) else "+"
    a_mag, b_mag = format(abs(a), "b"), format(abs(b), "b")

    pasos = [
        f"Regla de signos: ({_signo(a)}) × ({_signo(b)}) = {signo}",
        "",
        f"|A| = {a_mag}   ({abs(a)})",
        f"|B| = {b_mag}   ({abs(b)})",
        "",
        "Productos parciales (suma de desplazamientos):",
    ]

    acum = 0
    if b == 0:
        pasos.append("  |B| = 0  =>  producto = 0")
    else:
        for i, bit in enumerate(reversed(b_mag)):
            if bit == "1":                     # solo los bits en 1 aportan
                parcial = abs(a) << i
                acum += parcial
                pasos.append(f"  {a_mag} × 2^{i} = {a_mag} << {i} = {format(parcial, 'b')}")
        pasos += ["", f"Producto = {format(acum, 'b')}   (decimal: {acum})"]

    if signo == "-" and acum != 0:
        pasos.append(f"Resultado con signo: -{format(acum, 'b')}")
    return (-acum if signo == "-" else acum), pasos


# ----------------------------------------------------------------------
# División: regla de signos + restas sucesivas
# ----------------------------------------------------------------------
MAX_PASOS_DIV = 40      # límite de líneas mostradas para no saturar el panel


def dividir_c2_pasos(a_bin: str, b_bin: str):
    a, b = leer_c2(a_bin), leer_c2(b_bin)
    if b == 0:
        raise ZeroDivisionError("No se puede dividir entre cero.")

    signo = "-" if (a < 0) != (b < 0) else "+"
    cociente, residuo = divmod(abs(a), abs(b))

    pasos = [
        f"Regla de signos: ({_signo(a)}) ÷ ({_signo(b)}) = {signo}",
        "",
        f"|Dividendo| = {format(abs(a), 'b')}   ({abs(a)})",
        f"|Divisor|   = {format(abs(b), 'b')}   ({abs(b)})",
        "",
        "Restas sucesivas:",
    ]

    temp, k = abs(a), 0
    while temp >= abs(b) and k < MAX_PASOS_DIV:
        anterior = temp
        temp -= abs(b)
        k += 1
        pasos.append(
            f"  paso {k:>2}: {format(anterior, 'b')} - {format(abs(b), 'b')} = {format(temp, 'b')}"
        )
    if k >= MAX_PASOS_DIV:
        pasos.append(f"  ... (se omiten restas, cociente total = {cociente})")

    pasos += [
        "",
        f"Cociente = {format(cociente, 'b')}   (decimal: {cociente})",
        f"Residuo  = {format(residuo, 'b')}   (decimal: {residuo})",
    ]
    return (cociente if signo == "+" else -cociente), residuo, pasos


# ----------------------------------------------------------------------
# Operación genérica (cualquier base de entrada y de salida)
# ----------------------------------------------------------------------
def _dividir_truncado(a: int, b: int) -> int:
    """División entera truncada hacia cero (como en C)."""
    if b == 0:
        raise ZeroDivisionError("No se puede dividir entre cero.")
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


OPERACIONES = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "×": lambda a, b: a * b,
    "*": lambda a, b: a * b,
    "÷": _dividir_truncado,
    "/": _dividir_truncado,
}


def operar(a_str: str, base_a: int, b_str: str, base_b: int,
           base_out: int, op: str):
    """Devuelve (resultado_str, a_dec, b_dec, res_dec)."""
    if op not in OPERACIONES:
        raise ValueError(f"Operación desconocida: {op!r}")

    a = a_decimal(a_str, base_a)
    b = a_decimal(b_str, base_b)
    r = OPERACIONES[op](a, b)
    return desde_decimal(r, base_out), a, b, r
