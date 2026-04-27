# A) Palabras Reservadas (serie 1000)
PALABRAS_RESERVADAS: dict[str, int] = {
    "and":      1010, "as":       1020, "assert":   1030,
    "case":     1040, "class":    1050, "continue": 1060,
    "def":      1070, "del":      1080, "else":     1090,
    "except":   1100, "False":    1110, "finally":  1120,
    "for":      1130, "from":     1140, "global":   1150,
    "if":       1160, "import":   1170, "in":       1180,
    "is":       1190, "match":    1200, "None":     1210,
    "not":      1220, "pass":     1230, "raise":    1240,
    "return":   1250, "True":     1260, "try":      1270,
    "while":    1280, "with":     1290, "yield":    1300,
}
SIGUIENTE_PALABRA_RESERVADA = max(PALABRAS_RESERVADAS.values()) + 10

# B) Operadores (serie 2000) 
OPERADORES: dict[str, int] = {
    "+=": 2080, "/=": 2090,
    "/":  2010, "*":  2020, "+":  2030, "-":  2040,
    "<":  2050, ">":  2060, "=":  2070,
}
SIGUIENTE_OPERADOR = max(OPERADORES.values()) + 10

# C) Signos de puntuación (serie 3000)
SIGNOS_PUNTUACION: dict[str, int] = {
    ":":  3010, ",":  3020, ".":  3030,
    "\\": 3040, '"':  3050, "f\"": 3060,
}
SIGUIENTE_SIGNO = max(SIGNOS_PUNTUACION.values()) + 10

# D) Llaves (serie 4000)
LLAVES: dict[str, int] = {"{": 4010, "}": 4020}

# E) Paréntesis/Corchetes (serie 5000)
PARENTESIS: dict[str, int] = {
    "(": 5010, ")": 5020, "[": 5030, "]": 5040,
}

# F) Identificadores conocidos (serie 6000)
IDENTIFICADORES_CONOCIDOS: dict[str, int] = {
    "_": 6010, "__init__": 6020, "__str__": 6030,
    "a": 6040, "area": 6050, "b": 6060, "c": 6070,
    "classify": 6080, "closefd": 6090, "e": 6100,
    "file": 6110, "fileno": 6120, "global_counter": 6130,
    "hasattr": 6140, "is_valid": 6150, "isinstance": 6160,
    "label": 6170, "math": 6180, "name": 6190, "next": 6200,
    "open": 6210, "print": 6220, "process": 6230, "result": 6240,
    "s": 6250, "self": 6260, "Shape": 6270, "shape": 6280,
    "shapes": 6290, "sides": 6300, "sides_list": 6310,
    "sqrt": 6320, "stderr": 6330, "stdin": 6340, "sum": 6350,
    "super": 6360, "sys": 6370, "Triangle": 6380, "triangles": 6390,
    "value": 6400, "ValueError": 6410,
}
SIGUIENTE_IDENTIFICADOR = max(IDENTIFICADORES_CONOCIDOS.values()) + 10

# G) Constantes enteras (serie 7000)
TOKEN_ENTERO_DEC = 7010
TOKEN_ENTERO_NEG = 7020

# H) Constantes flotantes (serie 8000)
TOKEN_FLOTANTE = 8010

# Strings literales (serie 9000)
TOKEN_STRING = 9010
SIGUIENTE_STRING = 9020   # siguiente string nuevo → 9020, 9030…

# Nombres legibles 
NOMBRES: dict[int, str] = {
    1010:"PR:and",   1020:"PR:as",      1030:"PR:assert", 1040:"PR:case",
    1050:"PR:class", 1060:"PR:continue",1070:"PR:def",    1080:"PR:del",
    1090:"PR:else",  1100:"PR:except",  1110:"PR:False",  1120:"PR:finally",
    1130:"PR:for",   1140:"PR:from",    1150:"PR:global", 1160:"PR:if",
    1170:"PR:import",1180:"PR:in",      1190:"PR:is",     1200:"PR:match",
    1210:"PR:None",  1220:"PR:not",     1230:"PR:pass",   1240:"PR:raise",
    1250:"PR:return",1260:"PR:True",    1270:"PR:try",    1280:"PR:while",
    1290:"PR:with",  1300:"PR:yield",
    2010:"OP:/",  2020:"OP:*",  2030:"OP:+",  2040:"OP:-",
    2050:"OP:<",  2060:"OP:>",  2070:"OP:=",  2080:"OP:+=",2090:"OP:/=",
    3010:"SP::",  3020:"SP:,",  3030:"SP:.",  3040:"SP:\\",
    3050:'SP:"',  3060:'SP:f"',
    4010:"LV:{",  4020:"LV:}",
    5010:"PA:(",  5020:"PA:)",  5030:"PA:[",  5040:"PA:]",
    6010:"ID:_",          6020:"ID:__init__",  6030:"ID:__str__",
    6040:"ID:a",          6050:"ID:area",       6060:"ID:b",
    6070:"ID:c",          6080:"ID:classify",   6090:"ID:closefd",
    6100:"ID:e",          6110:"ID:file",        6120:"ID:fileno",
    6130:"ID:global_counter",6140:"ID:hasattr",  6150:"ID:is_valid",
    6160:"ID:isinstance", 6170:"ID:label",       6180:"ID:math",
    6190:"ID:name",       6200:"ID:next",        6210:"ID:open",
    6220:"ID:print",      6230:"ID:process",     6240:"ID:result",
    6250:"ID:s",          6260:"ID:self",        6270:"ID:Shape",
    6280:"ID:shape",      6290:"ID:shapes",      6300:"ID:sides",
    6310:"ID:sides_list", 6320:"ID:sqrt",        6330:"ID:stderr",
    6340:"ID:stdin",      6350:"ID:sum",         6360:"ID:super",
    6370:"ID:sys",        6380:"ID:Triangle",    6390:"ID:triangles",
    6400:"ID:value",      6410:"ID:ValueError",
    7010:"CE:entero",     7020:"CE:entero_neg",
    8010:"CF:flotante",
    9010:"STR:cadena",
}
