from dataclasses import dataclass, field
from tokens import (
    PALABRAS_RESERVADAS, SIGUIENTE_PALABRA_RESERVADA,
    OPERADORES, SIGUIENTE_OPERADOR,
    SIGNOS_PUNTUACION, SIGUIENTE_SIGNO,
    LLAVES, PARENTESIS,
    IDENTIFICADORES_CONOCIDOS, SIGUIENTE_IDENTIFICADOR,
    TOKEN_ENTERO_DEC, TOKEN_FLOTANTE,
    NOMBRES,
)

# ── Categoría de cada carácter ────────────────────────────────────────────────
_OP_CHARS = set('+-*/=<>!&|^~%@')
_ILEGALES = set('ñÑáéíóúüÁÉÍÓÚÜ')

def _cat(c: str) -> str:
    if c in _ILEGALES:          return 'ILG'
    if c.isdigit():             return 'DIG'
    if c.isalpha() or c == '_': return 'LET'
    if c in _OP_CHARS:          return 'OP'
    if c == '.':                return 'PNT'
    if c in SIGNOS_PUNTUACION:  return 'SIG'
    if c in LLAVES:             return 'LLV'
    if c in PARENTESIS:         return 'PAR'
    return 'UNK'

# ── Tabla de transición M[estado][categoría] → siguiente estado ───────────────
# Un estado sin entrada en M es estado final: se emite el token acumulado.
M: dict[str, dict[str, str]] = {
    'ID':  {'LET': 'ID',  'DIG': 'ID'},
    'NUM': {'DIG': 'NUM', 'PNT': 'FLT'},
    'FLT': {'DIG': 'FLT'},
    'OP':  {'OP':  'OP'},
}

# Estados de arranque por categoría (desde el estado inicial S)
_INICIO: dict[str, str] = {
    'LET': 'ID', 'DIG': 'NUM', 'OP': 'OP',
    'SIG': 'SIG', 'LLV': 'LLV', 'PAR': 'PAR',
}

# ── Dataclasses ───────────────────────────────────────────────────────────────
@dataclass
class TokenResultado:
    lexema: str; token: int; tipo: str; linea: int; columna: int

@dataclass
class ErrorLexico:
    caracter: str; linea: int; columna: int; mensaje: str

@dataclass
class ResultadoAnalisis:
    tokens:            list[TokenResultado] = field(default_factory=list)
    errores:           list[ErrorLexico]    = field(default_factory=list)
    nuevas_palabras:   dict[str, int]       = field(default_factory=dict)
    nuevos_operadores: dict[str, int]       = field(default_factory=dict)
    nuevos_signos:     dict[str, int]       = field(default_factory=dict)
    nuevos_ids:        dict[str, int]       = field(default_factory=dict)
    tokens_por_linea:  dict[int, list[int]] = field(default_factory=dict)


# ── Analizador léxico ─────────────────────────────────────────────────────────
class AnalizadorLexico:

    def __init__(self):
        self._reset()

    def _reset(self):
        self._sig_op = SIGUIENTE_OPERADOR
        self._sig_sp = SIGUIENTE_SIGNO
        self._sig_id = SIGUIENTE_IDENTIFICADOR
        self._nuevas_pr: dict[str, int] = {}
        self._nuevos_op: dict[str, int] = {}
        self._nuevos_sp: dict[str, int] = {}
        self._nuevos_id: dict[str, int] = {}

    # ── Entrada principal ─────────────────────────────────────────────────────
    def analizar(self, codigo: str) -> ResultadoAnalisis:
        self._reset()
        res = ResultadoAnalisis()
        for num_linea, linea in enumerate(codigo.splitlines(), start=1):
            res.tokens_por_linea[num_linea] = []
            self._analizar_linea(linea, num_linea, res)
        res.nuevas_palabras   = dict(self._nuevas_pr)
        res.nuevos_operadores = dict(self._nuevos_op)
        res.nuevos_signos     = dict(self._nuevos_sp)
        res.nuevos_ids        = dict(self._nuevos_id)
        return res

    # ── Autómata (algoritmo del profe corregido) ──────────────────────────────
    #
    #   flag = True  → leer siguiente dato (avanzar)
    #   flag = False → reusar dato actual  (no consumido)
    #   q0 se resetea a 'S' al inicio de cada token.
    #
    def _analizar_linea(self, linea: str, num_linea: int, res: ResultadoAnalisis):
        chars = linea          # secuencia de entrada (equivale al "archivo")
        n     = len(chars)
        i     = 0
        flag  = True
        dato  = ''

        while True:                          # Mientras !EOFC
            if flag:                         # leer dato
                if i >= n:
                    break
                dato  = chars[i]
                i    += 1
                flag  = False

            # Ignorar espacios/tabs entre tokens
            if dato in (' ', '\t'):
                flag = True
                continue

            # ── Inicio de un nuevo token ──────────────────────────────────────
            q0     = 'S'
            lexema = ''
            col    = i          # columna del primer carácter (i ya avanzó)

            while True:         # Mientras q0 ∉ F  (F = estados sin salida en M)
                cat = _cat(dato)

                # Carácter ilegal: registrar error, consumir y pasar al siguiente
                if cat == 'ILG':
                    res.errores.append(ErrorLexico(
                        caracter=dato, linea=num_linea, columna=col,
                        mensaje=f"Carácter ilegal '{dato}' -> no permitido",
                    ))
                    flag = True
                    break

                # Desde S: decidir el primer estado según categoría del dato
                if q0 == 'S':
                    q0 = _INICIO.get(cat, 'UNK')
                    if q0 == 'UNK':             # carácter desconocido
                        res.errores.append(ErrorLexico(
                            caracter=dato, linea=num_linea, columna=col,
                            mensaje=f"Carácter desconocido '{dato}'",
                        ))
                        flag = True
                        break
                    # Tokens de un solo carácter (SIG, LLV, PAR) → emitir ya
                    if q0 in ('SIG', 'LLV', 'PAR'):
                        lexema = dato
                        flag   = True
                        break
                    # Tokens multi-carácter: acumular primer carácter
                    lexema += dato
                    # Leer siguiente dato para continuar
                    if i < n:
                        dato  = chars[i]
                        i    += 1
                    else:
                        flag = True
                        break
                    continue

                # Intentar transición M[q0][cat]
                sig = M.get(q0, {}).get(cat)
                if sig:                         # transición válida → acumular
                    lexema += dato
                    q0      = sig
                    if i < n:
                        dato  = chars[i]
                        i    += 1
                    else:
                        flag = True
                        break
                else:                           # sin transición → token completo
                    flag = False                # reusar dato en el siguiente token
                    break

            # ── Emitir token ──────────────────────────────────────────────────
            if lexema and q0 not in ('S', 'UNK'):
                self._emitir(res, lexema, q0, num_linea, col)

    # ── Emitir según estado final ─────────────────────────────────────────────
    def _emitir(self, res: ResultadoAnalisis, lexema: str, estado: str,
                num_linea: int, col: int):
        match estado:
            case 'ID':
                tok, tipo = self._id(lexema)
            case 'NUM':
                tok, tipo = TOKEN_ENTERO_DEC, "Const. Entera"
            case 'FLT':
                tok, tipo = TOKEN_FLOTANTE, "Const. Flotante"
            case 'OP':
                tok, tipo = self._op(lexema)
            case 'SIG':
                tok, tipo = self._sig(lexema)
            case 'LLV':
                tok, tipo = LLAVES[lexema], "Llave"
            case 'PAR':
                tok, tipo = PARENTESIS[lexema], "Paréntesis"
            case _:
                return

        if tok not in NOMBRES:
            NOMBRES[tok] = f"{tipo}:{lexema}"
        res.tokens.append(TokenResultado(lexema, tok, tipo, num_linea, col))
        res.tokens_por_linea.setdefault(num_linea, []).append(tok)

    # ── Clasificadores ────────────────────────────────────────────────────────
    def _id(self, lex: str) -> tuple[int, str]:
        if lex in PALABRAS_RESERVADAS:    return PALABRAS_RESERVADAS[lex],    "Pal. Reservada"
        if lex in self._nuevas_pr:        return self._nuevas_pr[lex],        "Pal. Reservada*"
        if lex in IDENTIFICADORES_CONOCIDOS: return IDENTIFICADORES_CONOCIDOS[lex], "Identificador"
        if lex in self._nuevos_id:        return self._nuevos_id[lex],        "Identificador*"
        n = self._sig_id;  self._sig_id += 10
        self._nuevos_id[lex] = n;  NOMBRES[n] = f"ID*:{lex}"
        return n, "Identificador*"

    def _op(self, lex: str) -> tuple[int, str]:
        if lex in OPERADORES:       return OPERADORES[lex],       "Operador"
        if lex in self._nuevos_op:  return self._nuevos_op[lex],  "Operador*"
        n = self._sig_op;  self._sig_op += 10
        self._nuevos_op[lex] = n;  NOMBRES[n] = f"OP*:{lex}"
        return n, "Operador*"

    def _sig(self, lex: str) -> tuple[int, str]:
        if lex in SIGNOS_PUNTUACION:   return SIGNOS_PUNTUACION[lex],   "Signo Punc."
        if lex in self._nuevos_sp:     return self._nuevos_sp[lex],     "Signo Punc.*"
        n = self._sig_sp;  self._sig_sp += 10
        self._nuevos_sp[lex] = n;  NOMBRES[n] = f"SP*:{lex}"
        return n, "Signo Punc.*"