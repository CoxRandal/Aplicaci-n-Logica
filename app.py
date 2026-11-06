"""
Interfaz gráfica del conversor de bases numéricas.
Reutiliza toda la lógica del módulo conversiones.py.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from conversiones import (
    convertir, validar_numero,
    BASE_BIN, BASE_OCT, BASE_DEC, BASE_HEX,
)

# Etiquetas que se muestran en los combobox
NOMBRES = {
    BASE_DEC: "Decimal (10)",
    BASE_BIN: "Binario (2)",
    BASE_OCT: "Octal (8)",
    BASE_HEX: "Hexadecimal (16)",
}
# Etiquetas cortas para el historial y el detalle
NOMBRES_CORTOS = {
    BASE_DEC: "Decimal",
    BASE_BIN: "Binario",
    BASE_OCT: "Octal",
    BASE_HEX: "Hexadecimal",
}


class ConversorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Conversor de Bases Numéricas")
        self.root.geometry("640x660")
        self.root.minsize(580, 600)
        self._configurar_estilos()
        self._construir_ui()

    # ------------------------------------------------------------------
    # Estilos
    # ------------------------------------------------------------------
    def _configurar_estilos(self):
        estilo = ttk.Style()
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

    # ------------------------------------------------------------------
    # Construcción de la UI
    # ------------------------------------------------------------------
    def _construir_ui(self):
        contenedor = ttk.Frame(self.root, padding=18)
        contenedor.pack(fill="both", expand=True)

        # Encabezado
        ttk.Label(contenedor, text="Conversor de Bases Numéricas",
                  style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(contenedor,
                  text="Decimal · Binario · Octal · Hexadecimal",
                  style="Subtitulo.TLabel").pack(anchor="w", pady=(0, 14))

        # ------- Tarjeta de entrada -------
        tarjeta = ttk.LabelFrame(contenedor, text=" Datos de entrada ", padding=14)
        tarjeta.pack(fill="x")
        tarjeta.columnconfigure(1, weight=1)

        ttk.Label(tarjeta, text="Número:").grid(row=0, column=0, sticky="w", pady=4)
        self.var_numero = tk.StringVar()
        self.var_numero.trace_add("write", lambda *_: self._validar_en_vivo())
        self.entry_numero = ttk.Entry(tarjeta, textvariable=self.var_numero,
                                      font=("Consolas", 13))
        self.entry_numero.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)

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

        # Mensaje de validación en vivo
        self.lbl_validacion = ttk.Label(tarjeta, text="", style="Error.TLabel")
        self.lbl_validacion.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))

        # ------- Botones -------
        botones = ttk.Frame(contenedor)
        botones.pack(fill="x", pady=14)
        ttk.Button(botones, text="Convertir", style="Accion.TButton",
                   command=self.convertir).pack(side="left")
        ttk.Button(botones, text="Intercambiar bases",
                   command=self.intercambiar).pack(side="left", padx=8)
        ttk.Button(botones, text="Limpiar",
                   command=self.limpiar).pack(side="left")

        # ------- Resultado -------
        tarjeta_res = ttk.LabelFrame(contenedor, text=" Resultado ", padding=14)
        tarjeta_res.pack(fill="x")
        self.lbl_resultado = ttk.Label(tarjeta_res, text="—", style="Resultado.TLabel")
        self.lbl_resultado.pack(anchor="w")
        self.lbl_detalle = ttk.Label(tarjeta_res, text="", style="Subtitulo.TLabel")
        self.lbl_detalle.pack(anchor="w", pady=(4, 0))

        # ------- Historial -------
        tarjeta_hist = ttk.LabelFrame(contenedor, text=" Historial ", padding=10)
        tarjeta_hist.pack(fill="both", expand=True, pady=(14, 0))

        self.txt_historial = tk.Text(tarjeta_hist, height=7, state="disabled",
                                     font=("Consolas", 10), wrap="none",
                                     background="#fafafa", relief="flat")
        scroll = ttk.Scrollbar(tarjeta_hist, orient="vertical",
                               command=self.txt_historial.yview)
        self.txt_historial.configure(yscrollcommand=scroll.set)
        self.txt_historial.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Revalidar cuando cambia la base de origen
        self.var_origen.trace_add("write", lambda *_: self._validar_en_vivo())

        # Atajos: Enter convierte, Escape limpia
        self.root.bind("<Return>", lambda _e: self.convertir())
        self.root.bind("<Escape>", lambda _e: self.limpiar())
        self.entry_numero.focus_set()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _base_desde_etiqueta(etiqueta: str) -> int:
        for base, nombre in NOMBRES.items():
            if nombre == etiqueta:
                return base
        raise ValueError(f"Base desconocida: {etiqueta!r}")

    def _validar_en_vivo(self):
        """Muestra/oculta el error de formato mientras el usuario escribe."""
        texto = self.var_numero.get()
        if not texto.strip():
            self.lbl_validacion.config(text="")
            return
        try:
            base = self._base_desde_etiqueta(self.var_origen.get())
            validar_numero(texto, base)
            self.lbl_validacion.config(text="")
        except ValueError as e:
            self.lbl_validacion.config(text=str(e))

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    def convertir(self):
        texto = self.var_numero.get().strip()
        try:
            base_origen = self._base_desde_etiqueta(self.var_origen.get())
            base_destino = self._base_desde_etiqueta(self.var_destino.get())
            resultado = convertir(texto, base_origen, base_destino)
        except ValueError as e:
            messagebox.showerror("Error de conversión", str(e))
            self.lbl_resultado.config(text="—")
            self.lbl_detalle.config(text="")
            return

        self.lbl_resultado.config(text=resultado)
        self.lbl_detalle.config(
            text=f"{texto} ({NOMBRES_CORTOS[base_origen]})  =  "
                 f"{resultado} ({NOMBRES_CORTOS[base_destino]})"
        )
        self._agregar_historial(
            f"{texto:>14}  [{NOMBRES_CORTOS[base_origen]} -> "
            f"{NOMBRES_CORTOS[base_destino]}]  =  {resultado}"
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


def main():
    root = tk.Tk()
    ConversorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
