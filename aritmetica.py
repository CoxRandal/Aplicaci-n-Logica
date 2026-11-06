"""
Operaciones aritméticas con números con signo.
- Se trabaja con valores enteros (decimal como puente).
- Se incluyen algoritmos en complemento a dos (C2) que muestran el proceso paso a paso.
"""

from conversiones import a_decimal, desde_decimal


# ----------------------------------------------------------------------
# Complemento a dos
# ----------------------------------------------------------------------
def c2(valor: int, bits: int) -> str:
    """Representación de 'valor' (con signo) en complemento a dos de 'bits' bits."""
    rango = 1 << (bits - 1)
    if not (-rango <= valor < rango):
        raise ValueError(
            f"El valor {valor} no cabe en {bits} bits "
            f"(rango C2: -{rango} a {rango - 1})."
        )
    return format(valor & ((1 << bits) - 1), f"0{bits}b")


def leer_c2(bin_str: str) -> int:
    """Interpreta una cadena binaria como número con signo en C2."""
    v = int(bin_str, 2)
    if bin_str[0] == '1':
        v -= 1 << len(bin_str)
    return v


# ----------------------------------------------------------------------
# Suma en C2 (con pasos y detección de overflow)
# ----------------------------------------------------------------------
def suma_c2_pasos(a_bin: str, b_bin: str):
    bits = len(a_bin)
    a, b = int(a_bin, 2), int(b_bin, 2)
    res = format((a + b) & ((1 << bits) - 1), f"0{bits}b")
    overflow = (a_bin[0] == b_bin[0] and res[0] != a_bin[0])

    pasos = [
        f"  {a_bin}   ({leer_c2(a_bin):+d})",
        f"+ {b_bin}   ({leer_c2(b_bin):+d})",
        "  " + "-" * (bits + 8),
        f"  {res}   ({leer_c2(res):+d})",
    ]
    if overflow:
        pasos.append("")
        pasos.append("⚠ OVERFLOW: el resultado no cabe en los bits indicados.")
    return res, pasos


# ----------------------------------------------------------------------
# Resta en C2 (a - b = a + (-b))
# ----------------------------------------------------------------------
def resta_c2_pasos(a_bin: str, b_bin: str):
    bits = len(a_bin)
    inv_b = "".join('1' if c == '0' else '0' for c in b_bin)
    neg_b = format((int(inv_b, 2) + 1) & ((1 << bits) - 1), f"0{bits}b")

    res, pasos_c2 = suma_c2_pasos(a_bin, neg_b)
    encabezado = [
        "a - b   ==>   a + (-b)",
        f"-b = inv({b_bin}) + 1 = {inv_b} + 1 = {neg_b}",
        "",
    ]
    return res, encabezado + pasos_c2


# ----------------------------------------------------------------------
# Multiplicación (regla de signos + suma de productos parciales)
# ----------------------------------------------------------------------
def multiplicar_c2_pasos(a_bin: str, b_bin: str):
    a, b = leer_c2(a_bin), leer_c2(b_bin)
    signo = "-" if (a < 0) != (b < 0) else "+"
    a_abs, b_abs = abs(a), abs(b)
    a_mag = format(a_abs, "b")
    b_mag = format(b_abs, "b")

    pasos = [
        f"Regla de signos: ({'+' if a >= 0 else '-'}) × ({'+' if b >= 0 else '-'}) = {signo}",
        "",
        f"|A| = {a_mag}   ({a_abs})",
        f"|B| = {b_mag}   ({b_abs})",
        "",
        "Productos parciales (suma de desplazamientos):",
    ]
    acum = 0
    if b_abs == 0:
        pasos.append("  |B| = 0  =>  producto = 0")
    else:
        for i, bit in enumerate(reversed(b_mag)):
            if bit == '1':
                parc = a_abs << i
                acum += parc
                pasos.append(
                    f"  {a_mag} × 2^{i} = {a_mag} << {i} = {format(parc, 'b')}"
                )
        pasos.append("")
        pasos.append(f"Producto = {format(acum, 'b')}   (decimal: {acum})")
    if signo == "-" and acum != 0:
        pasos.append(f"Resultado con signo: -{format(acum, 'b')}")
    return (1 if signo == "+" else -1) * acum, pasos


# ----------------------------------------------------------------------
# División (regla de signos + restas sucesivas)
# ----------------------------------------------------------------------
def dividir_c2_pasos(a_bin: str, b_bin: str):
    a, b = leer_c2(a_bin), leer_c2(b_bin)
    if b == 0:
        raise ZeroDivisionError("No se puede dividir entre cero.")
    signo = "-" if (a < 0) != (b < 0) else "+"
    a_abs, b_abs = abs(a), abs(b)
    cociente, residuo = divmod(a_abs, b_abs)

    pasos = [
        f"Regla de signos: ({'+' if a >= 0 else '-'}) ÷ ({'+' if b >= 0 else '-'}) = {signo}",
        "",
        f"|Dividendo| = {format(a_abs, 'b')}   ({a_abs})",
        f"|Divisor|   = {format(b_abs, 'b')}   ({b_abs})",
        "",
        "Restas sucesivas:",
    ]
    temp, k = a_abs, 0
    # Limitamos las líneas mostradas para no saturar el panel
    while temp >= b_abs and k < 40:
        prev = temp
        temp -= b_abs
        k += 1
        pasos.append(
            f"  paso {k:>2}: {format(prev, 'b')} - {format(b_abs, 'b')} = {format(temp, 'b')}"
        )
    if k >= 40:
        pasos.append(f"  ... (se omiten restas, cociente total = {cociente})")
    pasos.append("")
    pasos.append(f"Cociente = {format(cociente, 'b')}   (decimal: {cociente})")
    pasos.append(f"Residuo  = {format(residuo, 'b')}   (decimal: {residuo})")
    resultado = cociente if signo == "+" else -cociente
    return resultado, residuo, pasos


# ----------------------------------------------------------------------
# Operación genérica (valores en cualquier base, resultado en cualquier base)
# ----------------------------------------------------------------------
def operar(a_str: str, base_a: int,
           b_str: str, base_b: int,
           base_out: int, op: str):
    """
    Realiza la operación aritmética y devuelve:
    (resultado_str, a_dec, b_dec, res_dec)
    La división es entera truncada hacia cero (como en C).
    """
    a = a_decimal(a_str, base_a)
    b = a_decimal(b_str, base_b)

    if op == '+':
        r = a + b
    elif op == '-':
        r = a - b
    elif op in ('×', '*'):
        r = a * b
    elif op in ('÷', '/'):
        if b == 0:
            raise ZeroDivisionError("No se puede dividir entre cero.")
        q = abs(a) // abs(b)
        r = q if (a >= 0) == (b >= 0) else -q
    else:
        raise ValueError(f"Operación desconocida: {op!r}")

    return desde_decimal(r, base_out), a, b, r
