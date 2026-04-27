
import re
from dataclasses import dataclass, field
from tokens import (
    PALABRAS_RESERVADAS, SIGUIENTE_PALABRA_RESERVADA,
    OPERADORES, SIGUIENTE_OPERADOR,
    SIGNOS_PUNTUACION, SIGUIENTE_SIGNO,
    LLAVES, PARENTESIS,
    IDENTIFICADORES_CONOCIDOS, SIGUIENTE_IDENTIFICADOR,
    TOKEN_ENTERO_DEC, TOKEN_ENTERO_NEG, TOKEN_FLOTANTE,
    TOKEN_STRING, SIGUIENTE_STRING,
    NOMBRES,
)

@dataclass
class TokenResultado:
    lexema:  str
    token:   int
    tipo:    str
    linea:   int
    columna: int

@dataclass
class ErrorLexico:
    caracter: str
    linea:    int
    columna:  int
    mensaje:  str

@dataclass
class ResultadoAnalisis:
    tokens:            list[TokenResultado] = field(default_factory=list)
    errores:           list[ErrorLexico]    = field(default_factory=list)
    # Tokens nuevos descubiertos
    nuevas_palabras:   dict[str, int] = field(default_factory=dict)
    nuevos_operadores: dict[str, int] = field(default_factory=dict)
    nuevos_signos:     dict[str, int] = field(default_factory=dict)
    nuevos_ids:        dict[str, int] = field(default_factory=dict)
    nuevos_strings:    dict[str, int] = field(default_factory=dict)
    # Tokens por línea 
    tokens_por_linea:  dict[int, list[int]] = field(default_factory=dict)

class AnalizadorLexico:
    RE_IDENTIFICADOR = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    RE_ILEGAL        = re.compile(r'[ñÑáéíóúüÁÉÍÓÚÜ]')
    def __init__(self):
        self._reset()
    def _reset(self):
        self._sig_pr  = SIGUIENTE_PALABRA_RESERVADA
        self._sig_op  = SIGUIENTE_OPERADOR
        self._sig_sp  = SIGUIENTE_SIGNO
        self._sig_id  = SIGUIENTE_IDENTIFICADOR
        self._sig_str = SIGUIENTE_STRING
        self._nuevas_pr:  dict[str, int] = {}
        self._nuevos_op:  dict[str, int] = {}
        self._nuevos_sp:  dict[str, int] = {}
        self._nuevos_id:  dict[str, int] = {}
        self._nuevos_str: dict[str, int] = {}

    def analizar(self, codigo: str) -> ResultadoAnalisis:
        self._reset()
        resultado = ResultadoAnalisis()
        lineas = codigo.splitlines()
        for num_linea, linea in enumerate(lineas, start=1):
            resultado.tokens_por_linea[num_linea] = []
            self._analizar_linea(linea, num_linea, resultado)
        resultado.nuevas_palabras   = dict(self._nuevas_pr)
        resultado.nuevos_operadores = dict(self._nuevos_op)
        resultado.nuevos_signos     = dict(self._nuevos_sp)
        resultado.nuevos_ids        = dict(self._nuevos_id)
        resultado.nuevos_strings    = dict(self._nuevos_str)
        return resultado

    def _analizar_linea(self, linea: str, num_linea: int, resultado: ResultadoAnalisis):
        i = 0
        n = len(linea)
        while i < n:
            # Espacios / tabs
            if linea[i] in (' ', '\t'):
                i += 1
                continue

            # Comentario -> resto ignorado
            if linea[i] == '#':
                break

            # Carácter ilegal suelto (ñ, etc.) —> fuera de identificador
            if self.RE_ILEGAL.match(linea[i]):
                resultado.errores.append(ErrorLexico(
                    caracter=linea[i], linea=num_linea, columna=i + 1,
                    mensaje=f"Carácter ilegal '{linea[i]}' -> no permitido en el lenguaje",
                ))
                i += 1
                continue

            # == f-string  f"..." ===
            if linea[i] == 'f' and i + 1 < n and linea[i + 1] == '"':
                # Consumir todo hasta el cierre
                j = i + 2
                while j < n and linea[j] != '"':
                    j += 1
                contenido = linea[i + 2:j]   # interior sin comillas
                lexema_completo = linea[i:j + 1] if j < n else linea[i:]
                tok = self._asignar_string(lexema_completo, resultado)
                self._agregar(resultado, lexema_completo, tok, "String", num_linea, i + 1)
                i = j + 1 if j < n else j
                continue

            # == String " ... "  ===
            if linea[i] == '"':
                j = i + 1
                while j < n and linea[j] != '"':
                    j += 1
                lexema_completo = linea[i:j + 1] if j < n else linea[i:]
                tok = self._asignar_string(lexema_completo, resultado)
                self._agregar(resultado, lexema_completo, tok, "String", num_linea, i + 1)
                i = j + 1 if j < n else j
                continue

            # == String ' ... '  ===
            if linea[i] == "'":
                j = i + 1
                while j < n and linea[j] != "'":
                    j += 1
                lexema_completo = linea[i:j + 1] if j < n else linea[i:]
                tok = self._asignar_string(lexema_completo, resultado)
                self._agregar(resultado, lexema_completo, tok, "String", num_linea, i + 1)
                i = j + 1 if j < n else j
                continue

            # == Operadores (detecta nuevos automáticamente) ===
            _OP_CHARS = set('+-*/=<>!&|^~%@')
            if linea[i] in _OP_CHARS:
                tok_op = None; largo_op = 0
                # 3 chars
                if i + 2 < n:
                    tres = linea[i:i + 3]
                    if tres in OPERADORES:
                        tok_op, largo_op = OPERADORES[tres], 3
                    elif tres in self._nuevos_op:
                        tok_op, largo_op = self._nuevos_op[tres], 3
                # 2 chars
                if tok_op is None and i + 1 < n:
                    dos = linea[i:i + 2]
                    if dos in OPERADORES:
                        tok_op, largo_op = OPERADORES[dos], 2
                    elif dos in self._nuevos_op:
                        tok_op, largo_op = self._nuevos_op[dos], 2
                # 1 char
                if tok_op is None:
                    uno_op = linea[i]
                    if uno_op in OPERADORES:
                        tok_op, largo_op = OPERADORES[uno_op], 1
                    elif uno_op in self._nuevos_op:
                        tok_op, largo_op = self._nuevos_op[uno_op], 1

                if tok_op is not None:
                    lexema_op = linea[i:i + largo_op]
                    tipo_op = "Operador" if lexema_op in OPERADORES else "Operador*"
                    self._agregar(resultado, lexema_op, tok_op, tipo_op, num_linea, i + 1)
                    i += largo_op; continue
                else:
                    # Operador nuevo: consumir todos los chars de operador contiguos
                    j = i
                    while j < n and linea[j] in _OP_CHARS:
                        j += 1
                    nuevo_lex = linea[i:j]
                    nuevo_num = self._sig_op
                    self._sig_op += 10
                    self._nuevos_op[nuevo_lex] = nuevo_num
                    NOMBRES[nuevo_num] = f"OP*:{nuevo_lex}"
                    resultado.nuevos_operadores[nuevo_lex] = nuevo_num
                    self._agregar(resultado, nuevo_lex, nuevo_num, "Operador*", num_linea, i + 1)
                    i = j; continue

            uno = linea[i]

            # == Llaves ===
            if uno in LLAVES:
                self._agregar(resultado, uno, LLAVES[uno], "Llave", num_linea, i + 1)
                i += 1; continue

            # == Paréntesis/Corchetes ===
            if uno in PARENTESIS:
                self._agregar(resultado, uno, PARENTESIS[uno], "Paréntesis", num_linea, i + 1)
                i += 1; continue

            # == Signos de puntuación ===
            if uno in SIGNOS_PUNTUACION:
                self._agregar(resultado, uno, SIGNOS_PUNTUACION[uno], "Signo Punc.", num_linea, i + 1)
                i += 1; continue

            # == Barra inversa ===
            if uno == '\\':
                self._agregar(resultado, uno, 3040, "Signo Punc.", num_linea, i + 1)
                i += 1; continue

            # == Número ===
            if uno.isdigit():
                j = i
                while j < n and linea[j].isdigit():
                    j += 1
                # ¿Flotante?
                if j < n and linea[j] == '.' and j + 1 < n and linea[j + 1].isdigit():
                    k = j + 1
                    while k < n and linea[k].isdigit():
                        k += 1
                    self._agregar(resultado, linea[i:k], TOKEN_FLOTANTE, "Const. Flotante", num_linea, i + 1)
                    i = k
                else:
                    self._agregar(resultado, linea[i:j], TOKEN_ENTERO_DEC, "Const. Entera", num_linea, i + 1)
                    i = j
                continue

            # == Identificador / Palabra reservada ===
            if uno.isalpha() or uno == '_':
                j = i
                while j < n and (linea[j].isalnum() or linea[j] == '_'):
                    j += 1
                lexema = linea[i:j]
                # ¿Tiene ñ u otro ilegal?
                m_ilegal = self.RE_ILEGAL.search(lexema)
                if m_ilegal:
                    resultado.errores.append(ErrorLexico(
                        caracter=m_ilegal.group(),
                        linea=num_linea, columna=i + 1 + m_ilegal.start(),
                        mensaje=f"Carácter ilegal '{m_ilegal.group()}' en '{lexema}'"
                                f" → la 'ñ' y vocales acentuadas no están permitidas",
                    ))
                    i = j; continue
                token, tipo = self._clasificar_id(lexema)
                self._agregar(resultado, lexema, token, tipo, num_linea, i + 1)
                i = j; continue

            # == Carácter desconocido ===
            resultado.errores.append(ErrorLexico(
                caracter=uno, linea=num_linea, columna=i + 1,
                mensaje=f"Carácter desconocido '{uno}'",
            ))
            i += 1

    # == Helpers ===
    def _agregar(self, resultado: ResultadoAnalisis,
                 lexema: str, token: int, tipo: str,
                 linea: int, columna: int):
        if token not in NOMBRES:
            NOMBRES[token] = f"{tipo}:{lexema}"
        tr = TokenResultado(lexema, token, tipo, linea, columna)
        resultado.tokens.append(tr)
        resultado.tokens_por_linea.setdefault(linea, []).append(token)

    def _clasificar_id(self, lexema: str) -> tuple[int, str]:
        if lexema in PALABRAS_RESERVADAS:
            return PALABRAS_RESERVADAS[lexema], "Pal. Reservada"
        if lexema in self._nuevas_pr:
            return self._nuevas_pr[lexema], "Pal. Reservada*"
        if lexema in IDENTIFICADORES_CONOCIDOS:
            return IDENTIFICADORES_CONOCIDOS[lexema], "Identificador"
        if lexema in self._nuevos_id:
            return self._nuevos_id[lexema], "Identificador*"
        nuevo = self._sig_id
        self._sig_id += 10
        self._nuevos_id[lexema] = nuevo
        NOMBRES[nuevo] = f"ID*:{lexema}"
        return nuevo, "Identificador*"

    def _asignar_string(self, lexema: str, resultado: ResultadoAnalisis) -> int:
        """Asigna token a un string literal. Siempre crea token nuevo por valor único."""
        if lexema in self._nuevos_str:
            return self._nuevos_str[lexema]
        # Primer string --> 9010, siguientes --> 9020, 9030 …
        if not self._nuevos_str:
            nuevo = TOKEN_STRING          # 9010
        else:
            nuevo = self._sig_str
            self._sig_str += 10
        self._nuevos_str[lexema] = nuevo
        NOMBRES[nuevo] = f"STR:{lexema[:20]}"
        resultado.nuevos_strings[lexema] = nuevo
        return nuevo
