import tkinter as tk
from tkinter import ttk, messagebox

import estilos as E
from analizador import AnalizadorLexico, ResultadoAnalisis
from tokens import NOMBRES


class InterfazAnalizador:
    def __init__(self, root: tk.Tk):
        self.root = root
        self._motor = AnalizadorLexico()
        self._ultimo: ResultadoAnalisis | None = None
        self._construir()

    # Construcción

    def _construir(self):
        self.root.title("Analizador Léxico")
        self.root.geometry(f"{E.VENTANA_W}x{E.VENTANA_H}")
        self.root.configure(bg=E.COLOR_FONDO)
        self.root.minsize(900, 560)
        self._barra_top()

        central = tk.Frame(self.root, bg=E.COLOR_FONDO)
        central.pack(fill="both", expand=True, padx=10, pady=(0, 6))
        central.columnconfigure(0, weight=1)
        central.columnconfigure(1, weight=1)
        central.rowconfigure(0, weight=1)

        self._panel_editor(central)
        self._panel_resultado(central)
        self._barra_estado()

    # Barra superior

    def _barra_top(self):
        barra = tk.Frame(self.root, bg=E.COLOR_HEADER, height=E.ALTO_HEADER)
        barra.pack(fill="x", pady=(0, 6))
        barra.pack_propagate(False)

        tk.Label(
            barra, text="Analizador Léxico",
            bg=E.COLOR_HEADER, fg=E.COLOR_TITULO,
            font=("Georgia", 15, "bold"),
        ).pack(side="left", padx=16)

        btn_frame = tk.Frame(barra, bg=E.COLOR_HEADER)
        btn_frame.pack(side="right", padx=12)

        self._btn(btn_frame, "Analizar", self._analizar).pack(side="left", padx=5)
        self._btn(btn_frame, "Errores",  self._ver_errores).pack(side="left", padx=5)
        self._btn(btn_frame, "Limpiar",  self._limpiar).pack(side="left", padx=5)

    def _btn(self, parent, texto, cmd):
        return tk.Button(
            parent, text=texto, command=cmd,
            font=E.FUENTE_BOTON, relief="flat", cursor="hand2",
            padx=14, pady=6,
        )

    # Panel izquierdo: editor

    def _panel_editor(self, parent):
        outer = tk.Frame(parent, bg=E.COLOR_BORDE_PANEL, bd=1, relief="solid")
        outer.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        outer.rowconfigure(1, weight=1)
        outer.columnconfigure(0, weight=1)

        hdr = tk.Frame(outer, bg=E.COLOR_HEADER, height=34)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew")
        hdr.grid_propagate(False)
        tk.Label(hdr, text=" Código fuente",
                 bg=E.COLOR_HEADER, fg=E.COLOR_SUBTITULO,
                 font=E.FUENTE_HEADER).pack(side="left", padx=6, pady=5)

        self.editor = tk.Text(
            outer, bg=E.COLOR_EDITOR, fg=E.COLOR_TEXTO_EDITOR,
            insertbackground="black", font=E.FUENTE_CODIGO,
            relief="flat", wrap="none", undo=True,
            selectbackground="#C7D9FF", padx=8, pady=4,
        )
        self.editor.grid(row=1, column=0, sticky="nsew")

        sb_v = ttk.Scrollbar(outer, orient="vertical", command=self.editor.yview)
        sb_v.grid(row=1, column=1, sticky="ns")
        self.editor.configure(yscrollcommand=sb_v.set)

        sb_h = ttk.Scrollbar(outer, orient="horizontal", command=self.editor.xview)
        sb_h.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.editor.configure(xscrollcommand=sb_h.set)

    # Panel derecho: tokens por línea

    def _panel_resultado(self, parent):
        outer = tk.Frame(parent, bg=E.COLOR_BORDE_PANEL, bd=1, relief="solid")
        outer.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        outer.rowconfigure(1, weight=1)
        outer.columnconfigure(0, weight=1)

        hdr = tk.Frame(outer, bg=E.COLOR_HEADER, height=34)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew")
        hdr.grid_propagate(False)
        tk.Label(hdr, text="  Tokens por línea",
                 bg=E.COLOR_HEADER, fg=E.COLOR_SUBTITULO,
                 font=E.FUENTE_HEADER).pack(side="left", padx=6, pady=5)
        self.lbl_conteo = tk.Label(hdr, text="",
                                   bg=E.COLOR_HEADER, fg=E.COLOR_SUBTITULO,
                                   font=E.FUENTE_INFO)
        self.lbl_conteo.pack(side="right", padx=12)

        self.txt_resultado = tk.Text(
            outer, bg=E.COLOR_RESULTADO, fg=E.COLOR_TEXTO_PANEL,
            font=E.FUENTE_RESULTADO, relief="flat", state="disabled",
            wrap="word", padx=16, pady=10,
            selectbackground="#C7D9FF",
        )
        sb_r = ttk.Scrollbar(outer, orient="vertical", command=self.txt_resultado.yview)
        self.txt_resultado.configure(yscrollcommand=sb_r.set)
        self.txt_resultado.grid(row=1, column=0, sticky="nsew")
        sb_r.grid(row=1, column=1, sticky="ns")

    # Barra de estado inferior

    def _barra_estado(self):
        bar = tk.Frame(self.root, bg=E.COLOR_HEADER, height=26)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        self.lbl_estado = tk.Label(
            bar, text="  Analizador Léxico  -  Automatas 1",
            bg=E.COLOR_HEADER, fg=E.COLOR_TEXTO_LINEA, font=E.FUENTE_INFO,
        )
        self.lbl_estado.pack(side="left")

    # Acciones

    def _analizar(self):
        codigo = self.editor.get("1.0", "end-1c")
        if not codigo.strip():
            messagebox.showinfo("Sin código", "Escribe o pega código en el panel izquierdo.")
            return

        r = self._motor.analizar(codigo)
        self._ultimo = r
        self._mostrar_resultado(r)
        n_tok = len(r.tokens)
        n_err = len(r.errores)

        if n_err:
            msg = f"  {n_tok} tokens  |  {n_err} error(es) léxico(s)."
        else:
            msg = f"  {n_tok} tokens  |  sin errores léxicos."
        self.lbl_estado.configure(text=msg)
        self.lbl_conteo.configure(text=f"{n_tok} tokens")

    def _ver_errores(self):
        if self._ultimo is None:
            messagebox.showinfo("Sin análisis", "Primero haz clic en Analizar.")
            return
        r = self._ultimo
        win = tk.Toplevel(self.root)
        win.title("Reporte")
        win.geometry("680x480")
        win.configure(bg=E.COLOR_FONDO)
        win.grab_set()

        hdr = tk.Frame(win, bg=E.COLOR_HEADER, height=40)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  Reporte de Errores y Tokens Nuevos",
                 bg=E.COLOR_HEADER, fg=E.COLOR_TITULO,
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=10, pady=8)

        frame = tk.Frame(win, bg=E.COLOR_FONDO)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        txt = tk.Text(frame, bg="#FFFFFF", fg="#000000", font=("Consolas", 11),
                      relief="flat", wrap="word", padx=16, pady=10)
        sb = ttk.Scrollbar(frame, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        txt.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        sep = "-" * 52 + "\n"

        def seccion(titulo):
            txt.insert("end", f"\n{titulo}\n")
            txt.insert("end", sep)

        seccion("ERRORES LEXICOS")
        if r.errores:
            for e in r.errores:
                txt.insert("end", f"  Ln {e.linea}, Col {e.columna}: {e.mensaje}\n")
        else:
            txt.insert("end", "  Sin errores léxicos.\n")

        seccion("OPERADORES NUEVOS (Serie 2000)")
        if r.nuevos_operadores:
            for lex, num in r.nuevos_operadores.items():
                txt.insert("end", f"  '{lex}'  ->  Token {num}\n")
        else:
            txt.insert("end", "  Todos los operadores estaban registrados.\n")

        seccion("IDENTIFICADORES NUEVOS (Serie 6000)")
        nuevos_todos = {**r.nuevos_ids, **r.nuevas_palabras}
        if nuevos_todos:
            for lex, num in nuevos_todos.items():
                txt.insert("end", f"  '{lex}'  ->  Token {num}\n")
        else:
            txt.insert("end", "  Todos los identificadores estaban registrados.\n")

        seccion("SIGNOS DE PUNTUACION NUEVOS (Serie 3000)")
        if r.nuevos_signos:
            for lex, num in r.nuevos_signos.items():
                txt.insert("end", f"  '{lex}'  ->  Token {num}\n")
        else:
            txt.insert("end", "  Todos los signos estaban registrados.\n")

        txt.configure(state="disabled")

        tk.Button(win, text="Cerrar", command=win.destroy,
                  font=E.FUENTE_BOTON, relief="flat", cursor="hand2",
                  padx=20, pady=6).pack(pady=(0, 10))

    def _limpiar(self):
        self.editor.delete("1.0", "end")
        self.txt_resultado.configure(state="normal")
        self.txt_resultado.delete("1.0", "end")
        self.txt_resultado.configure(state="disabled")
        self.lbl_conteo.configure(text="")
        self.lbl_estado.configure(text="  Listo.")
        self._ultimo = None

    # Mostrar tokens por línea (sin colores)

    def _mostrar_resultado(self, r: ResultadoAnalisis):
        self.txt_resultado.configure(state="normal")
        self.txt_resultado.delete("1.0", "end")

        codigo = self.editor.get("1.0", "end-1c")
        lineas = codigo.splitlines()

        for num_linea in range(1, len(lineas) + 1):
            tokens_en_linea = r.tokens_por_linea.get(num_linea, [])
            if not tokens_en_linea:
                self.txt_resultado.insert("end", "\n")
                continue
            self.txt_resultado.insert("end", " ".join(str(t) for t in tokens_en_linea) + "\n")

        self.txt_resultado.configure(state="disabled")