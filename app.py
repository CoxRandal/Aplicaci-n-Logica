"""Interfaz gráfica del proyecto: Conversiones + Aritmética."""

import tkinter as tk
from tkinter import ttk, messagebox

from conversiones import (convertir, validar_numero,
                          BASE_BIN, BASE_OCT, BASE_DEC, BASE_HEX)
from aritmetica import (c2, suma_c2_pasos, resta_c2_pasos,
                        multiplicar_c2_pasos, dividir_c2_pasos, operar)


# ----------------------------------------------------------------------
# Constantes / etiquetas
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
OPS = ["+   Suma", "-   Resta", "×   Multiplicación", "÷   División"]
BITS_OPCIONES = ["4", "8", "16", "32"]


def base_desde_etiqueta(etiqueta: str) -> int:
    for b, n in NOMBRES.items():
        if n == etiqueta:
            return b
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


# ======================================================================
# Pestaña 1: Conversiones (misma lógica que antes, ahora como Frame)
# ======================================================================
class ConversorFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=15)
        self._construir()

    def _construir(self):
        ttk.Label(self, text="Conversor de Bases Numéricas",
                  style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(self, text="Decimal · Binario · Octal · Hexadecimal",
                  style="Subtitulo.TLabel").pack(anchor="w", pady=(0, 12))

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
        ttk.Combobox(tarjeta, textvariable=self.var_origen, state="readonly",
                     values=list(NOMBRES.values()), width=20).grid(
            row=1, column=1, sticky="w", padx=(8, 0), pady=4)

        ttk.Label(tarjeta, text="Base destino:").grid(row=2, column=0, sticky="w", pady=4)
        self.var_destino = tk.StringVar(value=NOMBRES[BASE_BIN])
        ttk.Combobox(tarjeta, textvariable=self.var_destino, state="readonly",
                     values=list(NOMBRES.values()), width=20).grid(
            row=2, column=1, sticky="w", padx=(8, 0), pady=4)

        self.lbl_validacion = ttk.Label(tarjeta, text="", style="Error.TLabel")
        self.lbl_validacion.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))

        botones = ttk.Frame(self)
        botones.pack(fill="x", pady=14)
        ttk.Button(botones, text="Convertir", style="Accion.TButton",
                   command=self.convertir).pack(side="left")
        ttk.Button(botones, text="Intercambiar bases",
                   command=self.intercambiar).pack(side="left", padx=8)
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="left")

        res = ttk.LabelFrame(self, text=" Resultado ", padding=14)
        res.pack(fill="x")
        self.lbl_resultado = ttk.Label(res, text="—", style="Resultado.TLabel")
        self.lbl_resultado.pack(anchor="w")
        self.lbl_detalle = ttk.Label(res, text="", style="Subtitulo.TLabel")
        self.lbl_detalle.pack(anchor="w", pady=(4, 0))

        hist = ttk.LabelFrame(self, text=" Historial ", padding=10)
        hist.pack(fill="both", expand=True, pady=(14, 0))
        self.txt_historial = tk.Text(hist, height=6, state="disabled",
                                     font=("Consolas", 10), wrap="none",
                                     background="#fafafa", relief="flat")
        scroll = ttk.Scrollbar(hist, orient="vertical",
                               command=self.txt_historial.yview)
        self.txt_historial.configure(yscrollcommand=scroll.set)
        self.txt_historial.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.var_origen.trace_add("write", lambda *_: self._validar_en_vivo())
        self.entry_numero.focus_set()

    def _validar_en_vivo(self):
        texto = self.var_numero.get()
        if not texto.strip():
            self.lbl_validacion.config(text="")
            return
        try:
            validar_numero(texto, base_desde_etiqueta(self.var_origen.get()))
            self.lbl_validacion.config(text="")
        except ValueError as e:
            self.lbl_validacion.config(text=str(e))

    def convertir(self):
        texto = self.var_numero.get().strip()
        try:
            bo = base_desde_etiqueta(self.var_origen.get())
            bd = base_desde_etiqueta(self.var_destino.get())
            r = convertir(texto, bo, bd)
        except ValueError as e:
            messagebox.showerror("Error de conversión", str(e))
            self.lbl_resultado.config(text="—")
            self.lbl_detalle.config(text="")
            return

        self.lbl_resultado.config(text=r)
        self.lbl_detalle.config(
            text=f"{texto} ({NOMBRES_CORTOS[bo]})  =  {r} ({NOMBRES_CORTOS[bd]})"
        )
        self._agregar_historial(
            f"{texto:>14}  [{NOMBRES_CORTOS[bo]} -> {NOMBRES_CORTOS[bd]}]  =  {r}"
        )

    def intercambiar(self):
        o, d = self.var_origen.get(), self.var_destino.get()
        self.var_origen.set(d)
        self.var_destino.set(o)
        self._validar_en_vivo()

    def limpiar(self):
        self.var_numero.set("")
        self.lbl_resultado.config(text="—")
        self.lbl_detalle.config(text="")
        self.lbl_validacion.config(text="")
        self.entry_numero.focus_set()

    def _agregar_historial(self, linea: str):
        self.txt_historial.config(state="normal")
        self.txt_historial.insert("end", linea + "\n")
        self.txt_historial.see("end")
        self.txt_historial.config(state="disabled")


# ======================================================================
# Pestaña 2: Aritmética
# ======================================================================
class AritmeticaFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=15)
        self._construir()

    def _construir(self):
        ttk.Label(self, text="Operaciones aritméticas con signo",
                  style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(self,
                  text="Suma · Resta · Multiplicación · División · Complemento a dos",
                  style="Subtitulo.TLabel").pack(anchor="w", pady=(0, 12))

        # ------- Operandos -------
        frm = ttk.LabelFrame(self, text=" Operandos ", padding=12)
        frm.pack(fill="x")
        frm.columnconfigure(1, weight=1)

        ttk.Label(frm, text="Operando A:").grid(row=0, column=0, sticky="w", pady=3)
        self.var_a = tk.StringVar()
        entry_a = ttk.Entry(frm, textvariable=self.var_a, font=("Consolas", 12))
        entry_a.grid(row=0, column=1, sticky="ew", padx=(8, 8), pady=3)
        entry_a.bind("<Return>", lambda _e: self.calcular())
        self.var_base_a = tk.StringVar(value=NOMBRES[BASE_DEC])
        ttk.Combobox(frm, textvariable=self.var_base_a, state="readonly",
                     values=list(NOMBRES.values()), width=18).grid(row=0, column=2, pady=3)

        ttk.Label(frm, text="Operación:").grid(row=1, column=0, sticky="w", pady=3)
        self.var_op = tk.StringVar(value=OPS[0])
        ttk.Combobox(frm, textvariable=self.var_op, state="readonly",
                     values=OPS, width=22).grid(row=1, column=1, sticky="w",
                                                padx=(8, 8), pady=3)

        ttk.Label(frm, text="Operando B:").grid(row=2, column=0, sticky="w", pady=3)
        self.var_b = tk.StringVar()
        entry_b = ttk.Entry(frm, textvariable=self.var_b, font=("Consolas", 12))
        entry_b.grid(row=2, column=1, sticky="ew", padx=(8, 8), pady=3)
        entry_b.bind("<Return>", lambda _e: self.calcular())
        self.var_base_b = tk.StringVar(value=NOMBRES[BASE_DEC])
        ttk.Combobox(frm, textvariable=self.var_base_b, state="readonly",
                     values=list(NOMBRES.values()), width=18).grid(row=2, column=2, pady=3)

        ttk.Label(frm, text="Base resultado:").grid(row=3, column=0, sticky="w", pady=3)
        self.var_base_out = tk.StringVar(value=NOMBRES[BASE_DEC])
        ttk.Combobox(frm, textvariable=self.var_base_out, state="readonly",
                     values=list(NOMBRES.values()), width=22).grid(
            row=3, column=1, sticky="w", padx=(8, 8), pady=3)

        ttk.Label(frm, text="Bits para C2:").grid(row=4, column=0, sticky="w", pady=3)
        self.var_bits = tk.StringVar(value="8")
        ttk.Combobox(frm, textvariable=self.var_bits, state="readonly",
                     values=BITS_OPCIONES, width=10).grid(
            row=4, column=1, sticky="w", padx=(8, 8), pady=3)

        # ------- Botones -------
        btn = ttk.Frame(self)
        btn.pack(fill="x", pady=12)
        ttk.Button(btn, text="Calcular", style="Accion.TButton",
                   command=self.calcular).pack(side="left")
        ttk.Button(btn, text="Limpiar", command=self.limpiar).pack(side="left", padx=8)

        # ------- Resultado -------
        res = ttk.LabelFrame(self, text=" Resultado ", padding=12)
        res.pack(fill="x")
        self.lbl_resultado = ttk.Label(res, text="—", style="Resultado.TLabel")
        self.lbl_resultado.pack(anchor="w")
        self.lbl_detalle = ttk.Label(res, text="", style="Subtitulo.TLabel")
        self.lbl_detalle.pack(anchor="w", pady=(4, 0))

        # ------- Proceso C2 -------
        proc = ttk.LabelFrame(self, text=" Proceso paso a paso (complemento a dos) ",
                              padding=10)
        proc.pack(fill="both", expand=True, pady=(12, 0))
        self.txt_proceso = tk.Text(proc, height=12, state="disabled",
                                   font=("Consolas", 10), wrap="none",
                                   background="#fafafa", relief="flat")
        scroll = ttk.Scrollbar(proc, orient="vertical",
                               command=self.txt_proceso.yview)
        self.txt_proceso.configure(yscrollcommand=scroll.set)
        self.txt_proceso.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

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
            op = self.var_op.get()[0]          # '+', '-', '×' o '÷'
            bits = int(self.var_bits.get())

            validar_numero(a_str, base_a)
            validar_numero(b_str, base_b)

            res_str, a_dec, b_dec, res_dec = operar(
                a_str, base_a, b_str, base_b, base_out, op
            )
        except (ValueError, ZeroDivisionError) as e:
            messagebox.showerror("Error", str(e))
            self.lbl_resultado.config(text="—")
            self.lbl_detalle.config(text="")
            self._set_proceso("")
            return

        self.lbl_resultado.config(text=res_str)
        self.lbl_detalle.config(
            text=(f"{a_str} {op} {b_str}  =  {res_str}    "
                  f"(decimal: {a_dec} {op} {b_dec} = {res_dec})")
        )
        self._mostrar_proceso(a_dec, b_dec, op, bits)

    def limpiar(self):
        self.var_a.set("")
        self.var_b.set("")
        self.lbl_resultado.config(text="—")
        self.lbl_detalle.config(text="")
        self._set_proceso("")

    # ------------------------------------------------------------------
    # Panel de proceso
    # ------------------------------------------------------------------
    def _set_proceso(self, texto: str):
        self.txt_proceso.config(state="normal")
        self.txt_proceso.delete("1.0", "end")
        self.txt_proceso.insert("end", texto)
        self.txt_proceso.config(state="disabled")

    def _mostrar_proceso(self, a_dec: int, b_dec: int, op: str, bits: int):
        try:
            a_c2 = c2(a_dec, bits)
            b_c2 = c2(b_dec, bits)
        except ValueError as e:
            self._set_proceso(f"No se puede mostrar el proceso en {bits} bits:\n{e}")
            return

        lineas = [
            f"Bits: {bits}",
            f"A = {a_dec:>6}   ->   C2 = {a_c2}",
            f"B = {b_dec:>6}   ->   C2 = {b_c2}",
            "",
        ]

        try:
            if op == '+':
                _, pasos = suma_c2_pasos(a_c2, b_c2)
            elif op == '-':
                _, pasos = resta_c2_pasos(a_c2, b_c2)
            elif op == '×':
                _, pasos = multiplicar_c2_pasos(a_c2, b_c2)
            elif op == '÷':
                if b_dec == 0:
                    self._set_proceso("No se puede mostrar proceso: división entre cero.")
                    return
                _, _, pasos = dividir_c2_pasos(a_c2, b_c2)
            else:
                pasos = []
        except ZeroDivisionError:
            self._set_proceso("No se puede mostrar proceso: división entre cero.")
            return

        lineas.extend(pasos)
        self._set_proceso("\n".join(lineas))


# ======================================================================
# Ventana principal
# ======================================================================
def main():
    root = tk.Tk()
    root.title("Proyecto Estructuras Lógicas II")
    root.geometry("700x720")
    root.minsize(640, 660)

    estilo = ttk.Style()
    configurar_estilos(estilo)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    notebook.add(ConversorFrame(notebook), text="  Conversiones  ")
    notebook.add(AritmeticaFrame(notebook), text="  Aritmética  ")

    root.bind("<Escape>", lambda _e: root.focus_set())
    root.mainloop()


if __name__ == "__main__":
    main()
