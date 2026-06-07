"""
Alumno: Aitana Ortega Sánchez
Módulo para la normalización de expresiones horarias en castellano.
Incluye la función `normalizaHoras()` que lee un fichero de texto,
detecta expresiones horarias usando expresiones regulares y las convierte
al formato estándar HH:MM.
"""

import re


def _normaliza_expresion(match):
    texto = match.group(0)

    m = re.fullmatch(r'(\d{1,2}):(\d{2})', texto)
    if m:
        h, mn = int(m.group(1)), int(m.group(2))
        if 0 <= h <= 23 and 0 <= mn <= 59:
            return f'{h:02d}:{mn:02d}'
        return texto

    m = re.fullmatch(
        r'(\d{1,2})h(\d{1,2}m)?'
        r'(?:\s+(?:de\s+la\s+(?:mañana|tarde|noche|madrugada)|del\s+mediodía))?',
        texto
    )
    if m:
        h = int(m.group(1))
        mn = int(m.group(2)[:-1]) if m.group(2) else 0
        periodo = re.search(
            r'de\s+la\s+(mañana|tarde|noche|madrugada)|del\s+(mediodía)', texto
        )
        if periodo:
            p = periodo.group(1) or periodo.group(2)
            resultado = _aplica_periodo(h, mn, p)
            if resultado is None:
                return texto
            return resultado
        if 0 <= h <= 23 and 0 <= mn <= 59:
            return f'{h:02d}:{mn:02d}'
        return texto

    m = re.fullmatch(
        r'(\d{1,2})\s+(en\s+punto|y\s+cuarto|y\s+media|menos\s+cuarto)',
        texto
    )
    if m:
        h = int(m.group(1))
        fraccion = m.group(2)
        if not (1 <= h <= 12):
            return texto
        if 'menos cuarto' in fraccion:
            h, mn = h - 1, 45
        elif 'en punto' in fraccion:
            mn = 0
        elif 'y cuarto' in fraccion:
            mn = 15
        elif 'y media' in fraccion:
            mn = 30
        h = h % 12
        return f'{h:02d}:{mn:02d}'

    m = re.fullmatch(
        r'(\d{1,2})\s+(?:(en\s+punto|y\s+cuarto|y\s+media|menos\s+cuarto)\s+)?'
        r'(?:de\s+la\s+(?:mañana|tarde|noche|madrugada)|del\s+mediodía)',
        texto
    )
    if m:
        h = int(m.group(1))
        fraccion = m.group(2)
        if fraccion and 'menos cuarto' in fraccion:
            h_base, mn = h - 1, 45
        elif fraccion and 'y cuarto' in fraccion:
            h_base, mn = h, 15
        elif fraccion and 'y media' in fraccion:
            h_base, mn = h, 30
        else:
            h_base, mn = h, 0
        periodo = re.search(
            r'de\s+la\s+(mañana|tarde|noche|madrugada)|del\s+(mediodía)', texto
        )
        p = periodo.group(1) or periodo.group(2)
        resultado = _aplica_periodo(h_base, mn, p)
        if resultado is None:
            return texto
        return resultado

    return texto


def _aplica_periodo(h, mn, periodo):
    if mn < 0 or mn > 59:
        return None

    if periodo == 'mañana':
        if not (4 <= h <= 12):
            return None
        h_norm = h % 12
    elif periodo == 'mediodía':
        if h == 12:
            h_norm = 12
        elif 1 <= h <= 3:
            h_norm = h + 12
        else:
            return None
    elif periodo == 'tarde':
        if not (1 <= h <= 12):
            return None
        if not (3 <= h <= 8):
            return None
        h_norm = h + 12
    elif periodo == 'noche':
        if not (1 <= h <= 12):
            return None
        if h == 12:
            h_norm = 0
        elif 8 <= h <= 11:
            h_norm = h + 12
        elif 1 <= h <= 4:
            h_norm = h + 12
        else:
            return None
    elif periodo == 'madrugada':
        if not (1 <= h <= 6):
            return None
        h_norm = h
    else:
        return None

    if not (0 <= h_norm <= 23):
        return None
    return f'{h_norm:02d}:{mn:02d}'


PATRON = re.compile(
    r'\d{1,2}h(?:\d{1,2}m)?(?:\s+(?:de\s+la\s+(?:mañana|tarde|noche|madrugada)|del\s+mediodía))?'
    r'|\d{1,2}:\d{2}'
    r'|\d{1,2}\s+(?:en\s+punto|y\s+(?:cuarto|media)|menos\s+cuarto)'
    r'(?:\s+(?:de\s+la\s+(?:mañana|tarde|noche|madrugada)|del\s+mediodía))?'
    r'|\d{1,2}\s+(?:de\s+la\s+(?:mañana|tarde|noche|madrugada)|del\s+mediodía)',
    re.UNICODE
)


def normalizaHoras(ficText, ficNorm):
    """
    Lee el fichero de texto ficText, busca expresiones horarias en castellano
    y escribe ficNorm con esas expresiones convertidas al formato HH:MM.
    Las expresiones incorrectas se dejan tal cual.
    """
    with open(ficText, encoding='utf-8') as fin, \
         open(ficNorm, 'w', encoding='utf-8') as fout:
        for linea in fin:
            fout.write(PATRON.sub(_normaliza_expresion, linea))


if __name__ == '__main__':
    normalizaHoras('horas.txt', 'horas_norm.txt')
    with open('horas_norm.txt', encoding='utf-8') as f:
        print(f.read())