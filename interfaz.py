import tkinter as tk
from tkinter import ttk, messagebox
import re

import estilos as E
from analizador import AnalizadorLexico, ResultadoAnalisis
from tokens import NOMBRES

_KEYWORDS = {
    "and","as","assert","async","await","break","case","class",
    "continue","def","del","elif","else","except","False","finally",
    "for","from","global","if","import","in","is","lambda","match",
    "None","nonlocal","not","or","pass","raise","return","True","try",
    "while","with","yield",
}


class InterfazAnalizador:
    def __init__(self, root: tk.Tk):
        self.root = root
        self._motor = AnalizadorLexico()
        self._ultimo: ResultadoAnalisis | None = None
        self._construir()

    #  Construcción

    def _construir(self):
        self.root.title("Analizador Léxico")
        self.root.geometry(f"{E.VENTANA_W}x{E.VENTANA_H}")
        self.root.configure(bg=E.COLOR_FONDO)
        self.root.minsize(900, 560)
        self._barra_top()

        # Contenedor central
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

        self._btn(btn_frame, " Analizar",  self._analizar,  E.COLOR_BTN_ANALIZAR).pack(side="left", padx=5)
        self._btn(btn_frame, " Errores",   self._ver_errores, E.COLOR_BTN_ERRORES).pack(side="left", padx=5)
        self._btn(btn_frame, " Limpiar",   self._limpiar,   E.COLOR_BTN_LIMPIAR).pack(side="left", padx=5)

    def _btn(self, parent, texto, cmd, color):
        return tk.Button(
            parent, text=texto, command=cmd,
            bg=color, fg=E.COLOR_BTN_TEXTO,
            activebackground=color, activeforeground=E.COLOR_BTN_TEXTO,
            font=E.FUENTE_BOTON, relief="flat", cursor="hand2",
            padx=14, pady=6,
        )

    #  Panel izquierdo: editor
    def _panel_editor(self, parent):
        outer = tk.Frame(parent, bg=E.COLOR_BORDE_PANEL, bd=1, relief="solid")
        outer.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        outer.rowconfigure(1, weight=1)
        outer.columnconfigure(1, weight=1)

        # cabeza del panel
        hdr = tk.Frame(outer, bg=E.COLOR_HEADER, height=34)
        hdr.grid(row=0, column=0, columnspan=3, sticky="ew")
        hdr.grid_propagate(False)
        tk.Label(hdr, text=" Código fuente",
                 bg=E.COLOR_HEADER, fg=E.COLOR_SUBTITULO,
                 font=E.FUENTE_HEADER).pack(side="left", padx=6, pady=5)

        # Números de línea
        self.ln_text = tk.Text(
            outer, width=4, bg="#F0F2F5", fg=E.COLOR_TEXTO_LINEA,
            font=E.FUENTE_LINEAS, relief="flat", state="disabled",
            selectbackground="#F0F2F5", cursor="arrow",
        )
        self.ln_text.grid(row=1, column=0, sticky="ns", pady=(0, 0))

        # Separador vertical fino
        tk.Frame(outer, bg=E.COLOR_BORDE, width=1).grid(row=1, column=1, sticky="ns")

        # Editor principal
        self.editor = tk.Text(
            outer, bg=E.COLOR_EDITOR, fg=E.COLOR_TEXTO_EDITOR,
            insertbackground="#0057FF", font=E.FUENTE_CODIGO,
            relief="flat", wrap="none", undo=True,
            selectbackground="#C7D9FF", padx=8, pady=4,
        )
        self.editor.grid(row=1, column=2, sticky="nsew")

        # Scrollbars
        sb_v = ttk.Scrollbar(outer, orient="vertical", command=self._scroll_v)
        sb_v.grid(row=1, column=3, sticky="ns")
        self.editor.configure(yscrollcommand=sb_v.set)

        sb_h = ttk.Scrollbar(outer, orient="horizontal", command=self.editor.xview)
        sb_h.grid(row=2, column=0, columnspan=4, sticky="ew")
        self.editor.configure(xscrollcommand=sb_h.set)

        self.editor.bind("<KeyRelease>", self._on_key)
        self.editor.bind("<MouseWheel>", self._on_mwheel)

        # Tags syntax highlight
        self.editor.tag_configure("keyword",  foreground=E.COLOR_SH["keyword"])
        self.editor.tag_configure("number",   foreground=E.COLOR_SH["number"])
        self.editor.tag_configure("string",   foreground=E.COLOR_SH["string"])
        self.editor.tag_configure("comment",  foreground=E.COLOR_SH["comment"])
        self.editor.tag_configure("operator", foreground=E.COLOR_SH["operator"])

    # Panel derecho: resultado 
    def _panel_resultado(self, parent):
        outer = tk.Frame(parent, bg=E.COLOR_BORDE_PANEL, bd=1, relief="solid")
        outer.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        outer.rowconfigure(1, weight=1)
        outer.columnconfigure(0, weight=1)

        # cabeza 
        hdr = tk.Frame(outer, bg=E.COLOR_HEADER, height=34)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew")
        hdr.grid_propagate(False)
        tk.Label(hdr, text="  🏷  Tokens por línea",
                 bg=E.COLOR_HEADER, fg=E.COLOR_SUBTITULO,
                 font=E.FUENTE_HEADER).pack(side="left", padx=6, pady=5)
        self.lbl_conteo = tk.Label(hdr, text="",
                                   bg=E.COLOR_HEADER, fg="#A0C4FF",
                                   font=E.FUENTE_INFO)
        self.lbl_conteo.pack(side="right", padx=12)

        # Área de texto con los tokens por línea 
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
            bar, text="  Analizador Léxico Automatas 1 .",
            bg=E.COLOR_HEADER, fg=E.COLOR_TEXTO_LINEA, font=E.FUENTE_INFO,
        )
        self.lbl_estado.pack(side="left")

    #  Acciones
    def _analizar(self):
        codigo = self.editor.get("1.0", "end-1c")
        if not codigo.strip():
            messagebox.showinfo("Sin código", "Escribe o pega código en el panel izquierdo porfa.")
            return
        
        r = self._motor.analizar(codigo)
        self._ultimo = r
        self._mostrar_resultado(r)
        self._highlight_editor()
        n_err = len(r.errores)
        n_tok = len(r.tokens)

        # Alerta de valores desconocidos al analizar
        desconocidos = [e.caracter for e in r.errores]
        if desconocidos:
            lista = "  ".join(desconocidos)
            messagebox.showwarning(
                "Valores desconocidos",
                f"Se encontraron caracteres desconocidos en el codigo:\n\n  {lista}"
            )

        if n_err:
            msg = f"  Analisis completo: {n_tok} tokens, {n_err} valor(es) desconocido(s). Clic en Errores para ver detalles."
        else:
            msg = f"  Analisis completo: {n_tok} tokens, sin errores lexicos."
        self.lbl_estado.configure(text=msg)
        self.lbl_conteo.configure(text=f"{n_tok} tokens")

    def _ver_errores(self):
        if self._ultimo is None:
            messagebox.showinfo("Sin analisis", "Primero haz clic en Analizar :).")
            return
        r = self._ultimo
        win = tk.Toplevel(self.root)
        win.title("Reporte de Errores y Tokens Nuevos :)")
        win.geometry("700x500")
        win.configure(bg=E.COLOR_FONDO)
        win.grab_set()

        # cabeza de reporte
        hdr = tk.Frame(win, bg=E.COLOR_HEADER, height=40)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  Reporte de Errores y Tokens Nuevos",
                 bg=E.COLOR_HEADER, fg=E.COLOR_TITULO,
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=10, pady=8)

        # Area de texto
        frame = tk.Frame(win, bg=E.COLOR_FONDO)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        txt = tk.Text(frame, bg="#FFFFFF", fg="#1A1A2E", font=("Consolas", 11),
                      relief="flat", wrap="word", padx=16, pady=10)
        sb = ttk.Scrollbar(frame, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        txt.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        txt.tag_configure("seccion",  foreground="#7B2FBE", font=("Segoe UI", 11, "bold"))
        txt.tag_configure("linea_sep",foreground="#7B2FBE")
        txt.tag_configure("error",    foreground="#C84B31", font=("Consolas", 11))
        txt.tag_configure("nuevo",    foreground="#0057FF", font=("Consolas", 11))
        txt.tag_configure("ok",       foreground="#00B050", font=("Consolas", 11))

        sep = "-" * 52 + "\n"

        def seccion(titulo):
            txt.insert("end", f"\n{titulo}\n", "seccion")
            txt.insert("end", sep, "linea_sep")

        # ERRORES LEXICOS
        seccion("ERRORES LEXICOS")
        if r.errores:
            for e in r.errores:
                txt.insert("end", f"  Caracter desconocido  {e.caracter!r}\n", "error")
        else:
            txt.insert("end", "  Sin errores lexicos.\n", "ok")

        # OPERADORES NUEVOS
        seccion("OPERADORES NUEVOS (Serie 2000)")
        if r.nuevos_operadores:
            for lex, num in r.nuevos_operadores.items():
                txt.insert("end", f"  {lex}  -  Token {num}\n", "nuevo")
        else:
            txt.insert("end", "  Todos los operadores estaban registrados.\n", "ok")

        # IDENTIFICADORES NUEVOS
        seccion("IDENTIFICADORES NUEVOS")
        nuevos_ids_todos = {**r.nuevos_ids, **r.nuevas_palabras, **r.nuevos_signos}
        if nuevos_ids_todos:
            for lex, num in nuevos_ids_todos.items():
                txt.insert("end", f"  {lex}  -  Token {num}\n", "nuevo")
        else:
            txt.insert("end", "  Todos los identificadores estaban registrados.\n", "ok")

        # STRINGS DETECTADAS
        seccion("STRINGS / CADENAS DETECTADAS")
        if r.nuevos_strings:
            for lex, num in r.nuevos_strings.items():
                txt.insert("end", f"  {lex}  -  Token {num}\n", "nuevo")
        else:
            txt.insert("end", "  Ninguna cadena entre comillas detectada.\n", "ok")

        txt.configure(state="disabled")

        tk.Button(win, text="Cerrar", command=win.destroy,
                  bg=E.COLOR_BTN_LIMPIAR, fg="white",
                  font=E.FUENTE_BOTON, relief="flat", cursor="hand2",
                  padx=20, pady=6).pack(pady=(0, 10))

    def _limpiar(self):
        self.editor.delete("1.0", "end")
        self.txt_resultado.configure(state="normal")
        self.txt_resultado.delete("1.0", "end")
        self.txt_resultado.configure(state="disabled")
        self.lbl_conteo.configure(text="")
        self.lbl_estado.configure(text="  Listo.")
        self._actualizar_lineas()
        self._ultimo = None


    #  Mostrar resultado 
    def _mostrar_resultado(self, r: ResultadoAnalisis):
        self.txt_resultado.configure(state="normal")
        self.txt_resultado.delete("1.0", "end")

        # Tags de colores por categoría
        self.txt_resultado.tag_configure("PR",  foreground="#7B2FBE")   # Palabra Reservada
        self.txt_resultado.tag_configure("OP",  foreground="#D97706")   # Operadores
        self.txt_resultado.tag_configure("SP",  foreground="#1B7F4A")   # Signos
        self.txt_resultado.tag_configure("LV",  foreground="#C84B31")   # Llaves
        self.txt_resultado.tag_configure("PA",  foreground="#0057FF")   # Paréntesis
        self.txt_resultado.tag_configure("ID",  foreground="#1A1A2E")   # Identificador
        self.txt_resultado.tag_configure("IDN", foreground="#0057FF")   # ID nuevo
        self.txt_resultado.tag_configure("CE",  foreground="#C84B31")   # Num. entera
        self.txt_resultado.tag_configure("CF",  foreground="#C84B31")   # Num. flotante
        self.txt_resultado.tag_configure("STR", foreground="#1B7F4A")   # String
        self.txt_resultado.tag_configure("SPC", foreground="#9AA5B4")   # separador

        codigo = self.editor.get("1.0", "end-1c")
        lineas = codigo.splitlines()

        for num_linea, texto_linea in enumerate(lineas, start=1):
            tokens_en_linea = r.tokens_por_linea.get(num_linea, [])
            if not tokens_en_linea:
                # Línea vacía o solo comentario dejar un espacio
                self.txt_resultado.insert("end", "\n")
                continue

            for idx, tok_num in enumerate(tokens_en_linea):
                tag = self._tag_para(tok_num)
                self.txt_resultado.insert("end", str(tok_num), tag)
                if idx < len(tokens_en_linea) - 1:
                    self.txt_resultado.insert("end", " ", "SPC")
            self.txt_resultado.insert("end", "\n")

        self.txt_resultado.configure(state="disabled")

    def _tag_para(self, token: int) -> str:
        if 1000 <= token < 2000: return "PR"
        if 2000 <= token < 3000: return "OP"
        if 3000 <= token < 4000: return "SP"
        if 4000 <= token < 5000: return "LV"
        if 5000 <= token < 6000: return "PA"
        if 6000 <= token < 7000:
            # ¿Es nuevo (> 6410)?
            return "IDN" if token > 6410 else "ID"
        if 7000 <= token < 8000: return "CE"
        if 8000 <= token < 9000: return "CF"
        if token >= 9000:        return "STR"
        return "ID"

    #  Syntax highlight en el editor
    def _highlight_editor(self):
        for tag in ("keyword", "number", "string", "comment", "operator"):
            self.editor.tag_remove(tag, "1.0", "end")

        codigo = self.editor.get("1.0", "end")
        for i, linea in enumerate(codigo.split("\n"), start=1):
            # Comentarios
            m = re.search(r'#', linea)
            if m:
                self.editor.tag_add("comment", f"{i}.{m.start()}", f"{i}.end")
                linea = linea[:m.start()]
            # Strings
            for m in re.finditer(r"(f?\"[^\"]*\"|'[^']*')", linea):
                self.editor.tag_add("string", f"{i}.{m.start()}", f"{i}.{m.end()}")
            # Keywords
            for m in re.finditer(r'\b(' + '|'.join(_KEYWORDS) + r')\b', linea):
                self.editor.tag_add("keyword", f"{i}.{m.start()}", f"{i}.{m.end()}")
            # Números
            for m in re.finditer(r'\b\d+(\.\d+)?\b', linea):
                self.editor.tag_add("number", f"{i}.{m.start()}", f"{i}.{m.end()}")
            # Operadores
            for m in re.finditer(r'[+\-*/=<>]', linea):
                self.editor.tag_add("operator", f"{i}.{m.start()}", f"{i}.{m.end()}")

    #  Numeración de líneas y scroll
    def _actualizar_lineas(self, event=None):
        self.ln_text.configure(state="normal")
        self.ln_text.delete("1.0", "end")
        total = int(self.editor.index("end").split(".")[0]) - 1
        self.ln_text.insert("1.0", "\n".join(f"{i:>3}" for i in range(1, total + 1)))
        self.ln_text.configure(state="disabled")

    def _scroll_v(self, *args):
        self.editor.yview(*args)
        self.ln_text.yview(*args)

    def _on_mwheel(self, event):
        self.ln_text.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_key(self, event=None):
        self._actualizar_lineas()
