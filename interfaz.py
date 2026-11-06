"""Interfaz gráfica del proyecto: Conversiones + Aritmética."""

import tkinter as tk
from tkinter import ttk, messagebox

from conversiones import (convertir, validar_numero,
                          BASE_BIN, BASE_OCT, BASE_DEC, BASE_HEX)
from aritmetica import (c2, suma_c2_pasos, resta_c2_pasos,
                        multiplicar_c2_pasos, dividir_c2_pasos, operar)


# ----------------------------------------------------------------------
# Constantes
# ----------------------------------------------------------------------
NOMBRES = {
    BASE_DEC: "Decimal (10)",
    BASE_BIN: "Binario (2)",
    BASE_OCT: "Octal (8)",
    BASE_HEX: "Hexadecimal (16)",
}
NOMBRES_CORTOS = {
    BASE_DEC: "Decimal",
    BASE_BIN: "Binario",
    BASE_OCT: "Octal",
    BASE_HEX: "Hexadecimal",
}
BASE_POR_NOMBRE = {nombre: base for base, nombre in NOMBRES.items()}  # inverso

OPS = ["+   Suma", "-   Resta", "×   Multiplicación", "÷   División"]
BITS_OPCIONES = ["4", "8", "16", "32"]

# Cada operación -> función que genera el proceso. Todas devuelven los
# pasos como ÚLTIMO elemento de su resultado (por eso se usa [-1]).
FUNCIONES_PASOS = {
    "+": suma_c2_pasos,
    "-": resta_c2_pasos,
    "×": multiplicar_c2_pasos,
    "÷": dividir_c2_pasos,
}


def base_desde_etiqueta(etiqueta: str) -> int:
    try:
        return BASE_POR_NOMBRE[etiqueta]
    except KeyError:
        raise ValueError(f"Base desconocida: {etiqueta!r}")


def configurar_estilos(estilo: ttk.Style):
    try:
        estilo.theme_use("clam")
    except tk.TclError:
        pass
    estilo.configure("Titulo.TLabel", font=("Segoe UI", 16, "bold"))
    estilo.configure("Subtitulo.TLabel", font=("Segoe UI", 10), foreground="#555")
    estilo.configure("Resultado.TLabel",
                     font=("Consolas", 22, "bold"), foreground="#0a6")
    estilo.configure("Error.TLabel", foreground="#c00")
    estilo.configure("Accion.TButton", font=("Segoe UI", 10, "bold"))


# ----------------------------------------------------------------------
# Helpers de widgets (evitan repetir código en las dos pestañas)
# ----------------------------------------------------------------------
def crear_combo(padre, variable, valores, ancho):
    return ttk.Combobox(padre, textvariable=variable, state="readonly",
                        values=valores, width=ancho)


def crear_texto(padre, alto):
    """Cuadro de texto de solo lectura con scroll vertical."""
    txt = tk.Text(padre, height=alto, state="disabled", font=("Consolas", 10),
                  wrap="none", background="#fafafa", relief="flat")
    scroll = ttk.Scrollbar(padre, orient="vertical", command=txt.yview)
    txt.configure(yscrollcommand=scroll.set)
    txt.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return txt


def escribir(txt, texto, reemplazar=True):
    """Escribe en un Text de solo lectura (reemplazando o agregando al final)."""
    txt.config(state="normal")
    if reemplazar:
        txt.delete("1.0", "end")
    txt.insert("end", texto)
    txt.see("end")
    txt.config(state="disabled")


# ======================================================================
# Base común: encabezado + panel de resultado
# ======================================================================
class PestanaBase(ttk.Frame):
    def __init__(self, master, titulo, subtitulo):
        super().__init__(master, padding=15)
        ttk.Label(self, text=titulo, style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(self, text=subtitulo,
                  style="Subtitulo.TLabel").pack(anchor="w", pady=(0, 12))
        self._construir()

    def _crear_panel_resultado(self, padding):
        res = ttk.LabelFrame(self, text=" Resultado ", padding=padding)
        res.pack(fill="x")
        self.lbl_resultado = ttk.Label(res, text="—", style="Resultado.TLabel")
        self.lbl_resultado.pack(anchor="w")
        self.lbl_detalle = ttk.Label(res, text="", style="Subtitulo.TLabel")
        self.lbl_detalle.pack(anchor="w", pady=(4, 0))

    def _mostrar_resultado(self, resultado="—", detalle=""):
        self.lbl_resultado.config(text=resultado)
        self.lbl_detalle.config(text=detalle)


# ======================================================================
# Pestaña 1: Conversiones
# ======================================================================
class ConversorFrame(PestanaBase):
    def __init__(self, master):
        super().__init__(master, "Conversor de Bases Numéricas",
                         "Decimal · Binario · Octal · Hexadecimal")

    def _construir(self):
        # ------- Entrada -------
        tarjeta = ttk.LabelFrame(self, text=" Datos de entrada ", padding=14)
        tarjeta.pack(fill="x")
        tarjeta.columnconfigure(1, weight=1)

        ttk.Label(tarjeta, text="Número:").grid(row=0, column=0, sticky="w", pady=4)
        self.var_numero = tk.StringVar()
        self.var_numero.trace_add("write", lambda *_: self._validar_en_vivo())
        self.entry_numero = ttk.Entry(tarjeta, textvariable=self.var_numero,
                                      font=("Consolas", 13))
        self.entry_numero.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)
        self.entry_numero.bind("<Return>", lambda _e: self.convertir())

        ttk.Label(tarjeta, text="Base origen:").grid(row=1, column=0, sticky="w", pady=4)
        self.var_origen = tk.StringVar(value=NOMBRES[BASE_DEC])
        crear_combo(tarjeta, self.var_origen, list(NOMBRES.values()), 20).grid(
            row=1, column=1, sticky="w", padx=(8, 0), pady=4)

        ttk.Label(tarjeta, text="Base destino:").grid(row=2, column=0, sticky="w", pady=4)
        self.var_destino = tk.StringVar(value=NOMBRES[BASE_BIN])
        crear_combo(tarjeta, self.var_destino, list(NOMBRES.values()), 20).grid(
            row=2, column=1, sticky="w", padx=(8, 0), pady=4)

        self.lbl_validacion = ttk.Label(tarjeta, text="", style="Error.TLabel")
        self.lbl_validacion.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))

        # ------- Botones -------
        botones = ttk.Frame(self)
        botones.pack(fill="x", pady=14)
        ttk.Button(botones, text="Convertir", style="Accion.TButton",
                   command=self.convertir).pack(side="left")
        ttk.Button(botones, text="Intercambiar bases",
                   command=self.intercambiar).pack(side="left", padx=8)
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="left")

        # ------- Resultado e historial -------
        self._crear_panel_resultado(padding=14)

        hist = ttk.LabelFrame(self, text=" Historial ", padding=10)
        hist.pack(fill="both", expand=True, pady=(14, 0))
        self.txt_historial = crear_texto(hist, alto=6)

        self.var_origen.trace_add("write", lambda *_: self._validar_en_vivo())
        self.entry_numero.focus_set()

    def _validar_en_vivo(self):
        texto = self.var_numero.get()
        mensaje = ""
        if texto.strip():
            try:
                validar_numero(texto, base_desde_etiqueta(self.var_origen.get()))
            except ValueError as e:
                mensaje = str(e)
        self.lbl_validacion.config(text=mensaje)

    def convertir(self):
        texto = self.var_numero.get().strip()
        try:
            bo = base_desde_etiqueta(self.var_origen.get())
            bd = base_desde_etiqueta(self.var_destino.get())
            r = convertir(texto, bo, bd)
        except ValueError as e:
            messagebox.showerror("Error de conversión", str(e))
            self._mostrar_resultado()
            return

        self._mostrar_resultado(
            r, f"{texto} ({NOMBRES_CORTOS[bo]})  =  {r} ({NOMBRES_CORTOS[bd]})")
        escribir(self.txt_historial,
                 f"{texto:>14}  [{NOMBRES_CORTOS[bo]} -> {NOMBRES_CORTOS[bd]}]  =  {r}\n",
                 reemplazar=False)

    def intercambiar(self):
        o, d = self.var_origen.get(), self.var_destino.get()
        self.var_origen.set(d)
        self.var_destino.set(o)

    def limpiar(self):
        self.var_numero.set("")              # esto ya dispara _validar_en_vivo
        self._mostrar_resultado()
        self.entry_numero.focus_set()


# ======================================================================
# Pestaña 2: Aritmética
# ======================================================================
class AritmeticaFrame(PestanaBase):
    def __init__(self, master):
        super().__init__(
            master, "Operaciones aritméticas con signo",
            "Suma · Resta · Multiplicación · División · Complemento a dos")

    def _construir(self):
        frm = ttk.LabelFrame(self, text=" Operandos ", padding=12)
        frm.pack(fill="x")
        frm.columnconfigure(1, weight=1)

        valores_bases = list(NOMBRES.values())

        # Operando A, operación, operando B
        self.var_a, self.var_base_a = self._fila_operando(frm, 0, "Operando A:")
        ttk.Label(frm, text="Operación:").grid(row=1, column=0, sticky="w", pady=3)
        self.var_op = tk.StringVar(value=OPS[0])
        crear_combo(frm, self.var_op, OPS, 22).grid(
            row=1, column=1, sticky="w", padx=(8, 8), pady=3)
        self.var_b, self.var_base_b = self._fila_operando(frm, 2, "Operando B:")

        # Opciones del resultado
        ttk.Label(frm, text="Base resultado:").grid(row=3, column=0, sticky="w", pady=3)
        self.var_base_out = tk.StringVar(value=NOMBRES[BASE_DEC])
        crear_combo(frm, self.var_base_out, valores_bases, 22).grid(
            row=3, column=1, sticky="w", padx=(8, 8), pady=3)

        ttk.Label(frm, text="Bits para C2:").grid(row=4, column=0, sticky="w", pady=3)
        self.var_bits = tk.StringVar(value="8")
        crear_combo(frm, self.var_bits, BITS_OPCIONES, 10).grid(
            row=4, column=1, sticky="w", padx=(8, 8), pady=3)

        # Botones
        btn = ttk.Frame(self)
        btn.pack(fill="x", pady=12)
        ttk.Button(btn, text="Calcular", style="Accion.TButton",
                   command=self.calcular).pack(side="left")
        ttk.Button(btn, text="Limpiar", command=self.limpiar).pack(side="left", padx=8)

        # Resultado y proceso
        self._crear_panel_resultado(padding=12)

        proc = ttk.LabelFrame(self, text=" Proceso paso a paso (complemento a dos) ",
                              padding=10)
        proc.pack(fill="both", expand=True, pady=(12, 0))
        self.txt_proceso = crear_texto(proc, alto=12)

    def _fila_operando(self, padre, fila, etiqueta):
        """Crea: etiqueta + entrada + combo de base. Devuelve (var_valor, var_base)."""
        ttk.Label(padre, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=3)
        var = tk.StringVar()
        entry = ttk.Entry(padre, textvariable=var, font=("Consolas", 12))
        entry.grid(row=fila, column=1, sticky="ew", padx=(8, 8), pady=3)
        entry.bind("<Return>", lambda _e: self.calcular())

        var_base = tk.StringVar(value=NOMBRES[BASE_DEC])
        crear_combo(padre, var_base, list(NOMBRES.values()), 18).grid(
            row=fila, column=2, pady=3)
        return var, var_base

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    def calcular(self):
        try:
            a_str = self.var_a.get().strip()
            b_str = self.var_b.get().strip()
            base_a = base_desde_etiqueta(self.var_base_a.get())
            base_b = base_desde_etiqueta(self.var_base_b.get())
            base_out = base_desde_etiqueta(self.var_base_out.get())
            op = self.var_op.get()[0]            # '+', '-', '×' o '÷'
            bits = int(self.var_bits.get())

            validar_numero(a_str, base_a)
            validar_numero(b_str, base_b)
            res_str, a_dec, b_dec, res_dec = operar(
                a_str, base_a, b_str, base_b, base_out, op)
        except (ValueError, ZeroDivisionError) as e:
            messagebox.showerror("Error", str(e))
            self._mostrar_resultado()
            escribir(self.txt_proceso, "")
            return

        self._mostrar_resultado(
            res_str,
            f"{a_str} {op} {b_str}  =  {res_str}    "
            f"(decimal: {a_dec} {op} {b_dec} = {res_dec})")
        self._mostrar_proceso(a_dec, b_dec, op, bits)

    def limpiar(self):
        self.var_a.set("")
        self.var_b.set("")
        self._mostrar_resultado()
        escribir(self.txt_proceso, "")

    def _mostrar_proceso(self, a_dec, b_dec, op, bits):
        try:
            a_c2, b_c2 = c2(a_dec, bits), c2(b_dec, bits)
            pasos = FUNCIONES_PASOS[op](a_c2, b_c2)[-1]
        except ValueError as e:
            escribir(self.txt_proceso,
                     f"No se puede mostrar el proceso en {bits} bits:\n{e}")
            return
        except ZeroDivisionError:
            escribir(self.txt_proceso,
                     "No se puede mostrar proceso: división entre cero.")
            return

        encabezado = [
            f"Bits: {bits}",
            f"A = {a_dec:>6}   ->   C2 = {a_c2}",
            f"B = {b_dec:>6}   ->   C2 = {b_c2}",
            "",
        ]
        escribir(self.txt_proceso, "\n".join(encabezado + pasos))


# ======================================================================
# Ventana principal
# ======================================================================
def main():
    root = tk.Tk()
    root.title("Proyecto Estructuras Lógicas II")
    root.geometry("700x720")
    root.minsize(640, 660)

    configurar_estilos(ttk.Style())

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    notebook.add(ConversorFrame(notebook), text="  Conversiones  ")
    notebook.add(AritmeticaFrame(notebook), text="  Aritmética  ")

    root.bind("<Escape>", lambda _e: root.focus_set())
    root.mainloop()


if __name__ == "__main__":
    main()
