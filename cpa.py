"""
Explicaciones CPA (Concreto -> Pictorico -> Abstracto) para Math Quest.

El metodo CPA es el estandar en matematicas de primaria (Singapur / Bruner):
antes de llegar al numero abstracto, el nino necesita ver el concepto como
material manipulable (concreto) y luego como dibujo (pictorico).

Cada funcion devuelve el HTML interior de la caja de pista. La estructura es
siempre la misma y en ese orden:

    1. CONCRETO   -> que significa la operacion, con objetos contables
    2. PICTORICO  -> la representacion visual (bloques, barras, rejilla)
    3. ABSTRACTO  -> el razonamiento en simbolos y, al final, el resultado

La respuesta va SIEMPRE de ultima y marcada como conclusion, nunca sola:
si el nino solo lee el numero no aprendio nada, y ese era el problema de la
version anterior.

Todas las funciones son bilingues via el parametro `lang` ("Español"/"English").
"""

# El generador produce hasta 9 filas x 10 columnas (90 bloques), y esa rejilla
# completa SI se dibuja: es justo el caso donde el nino mas necesita ver la
# estructura. El bloque se encoge segun el ancho para que quepa en tablet.
MAX_FILAS = 12
MAX_COLUMNAS = 12


def _seccion(titulo, cuerpo):
    """Un paso de la explicacion: etiqueta pequena + contenido."""
    return (
        f'<div class="cpa-step">'
        f'<span class="cpa-step-label">{titulo}</span>'
        f'<div class="cpa-step-body">{cuerpo}</div>'
        f'</div>'
    )


def _resultado(etiqueta, valor):
    """La respuesta, siempre como cierre y visualmente separada."""
    return f'<div class="cpa-result">{etiqueta} <b>{valor}</b></div>'


def _rejilla(filas, columnas, emoji="\U0001f7e6", en=False, rotulos=True):
    """Rejilla de multiplicacion: una fila por grupo, rotulada.

    Cada convencion del dibujo va explicada, porque una rejilla sin leyenda
    es un jeroglifico: el numero de la izquierda es el grupo, la columna de
    la derecha es el total acumulado hasta esa fila.
    """
    if filas > MAX_FILAS or columnas > MAX_COLUMNAS:
        return None

    escala = " sm" if columnas > 8 else ""

    lineas = []
    for i in range(1, filas + 1):
        bloques = "".join(
            '<i class="cpa-blk">' + emoji + "</i>" for _ in range(columnas)
        )
        lineas.append(
            '<div class="cpa-row">'
            '<span class="cpa-row-n">' + str(i) + "</span>"
            '<span class="cpa-blocks">' + bloques + "</span>"
            '<span class="cpa-count">' + str(i * columnas) + "</span>"
            "</div>"
        )

    if not rotulos:
        return '<div class="cpa-grid' + escala + '">' + "".join(lineas) + "</div>"

    cab = (
        '<div class="cpa-grid-head">'
        '<span class="cpa-h-n">' + ("group" if en else "grupo") + "</span>"
        '<span class="cpa-h-b">'
        + (str(columnas) + " in each row" if en else str(columnas) + " en cada fila")
        + "</span>"
        '<span class="cpa-h-c">' + ("running total" if en else "vas contando") + "</span>"
        "</div>"
    )
    return ('<div class="cpa-grid' + escala + '">'
            + cab + "".join(lineas) + "</div>")



def _rect_perimetro(ancho, largo, en):
    """Rectangulo dibujado con bloques en el BORDE, no relleno.

    Es la imagen que separa perimetro de area: aqui solo se pinta la orilla,
    que es justo lo que se mide y se suma.
    """
    a = min(ancho, 8)
    l = min(largo, 12)
    filas = []
    for f in range(a):
        if f == 0 or f == a - 1:
            fila = "\U0001f7e6" * l                       # borde superior/inferior
        else:
            fila = "\U0001f7e6" + "\u2b1c" * (l - 2) + "\U0001f7e6"   # solo los lados
        filas.append('<div class="cpa-row"><span class="cpa-blocks">'
                     + "".join('<i class="cpa-blk">' + c + "</i>" for c in fila)
                     + "</span></div>")
    escala = " sm" if l > 8 else ""  # el borde no usa rotulos de grupo
    etiqueta = ("width" if en else "ancho") + " " + str(ancho)
    etiqueta_l = ("length" if en else "largo") + " " + str(largo)
    return ('<div class="cpa-figure">'
            '<div class="cpa-fig-top">&#8595; ' + etiqueta_l + "</div>"
            '<div class="cpa-grid' + escala + '">' + "".join(filas) + "</div>"
            '<div class="cpa-fig-side">' + etiqueta + "</div>"
            "</div>")


def _triangulo(l1, l2, l3, en):
    """Triangulo a escala aproximada con los 3 lados rotulados."""
    return ('<svg class="cpa-svg" viewBox="0 0 200 120" role="img">'
            '<polygon points="100,12 188,104 12,104" '
            'fill="#dbeafe" stroke="#2563eb" stroke-width="4" '
            'stroke-linejoin="round"/>'
            '<text x="42" y="50" class="cpa-svg-t">' + str(l1) + "</text>"
            '<text x="150" y="50" class="cpa-svg-t">' + str(l2) + "</text>"
            '<text x="100" y="119" class="cpa-svg-t">' + str(l3) + "</text>"
            "</svg>")



def _reparto(total, grupos, cada, en):
    """Dibuja la division como reparto: N cajas, cada una con su contenido.

    A diferencia de la rejilla de multiplicacion, aqui cada fila se rotula
    explicitamente como un grupo ("Grupo 1") y se dice cuanto le toca, que es
    la pregunta que responde una division.
    """
    if grupos > MAX_FILAS or cada > MAX_COLUMNAS:
        return None

    etiq = "Group" if en else "Grupo"
    cada_txt = ("gets" if en else "recibe") + " " + str(cada)
    escala = " sm" if cada > 8 else ""

    filas = []
    for g in range(1, grupos + 1):
        bloques = "".join(
            '<i class="cpa-blk">\U0001f7e8</i>' for _ in range(cada)
        )
        filas.append(
            '<div class="cpa-share-row">'
            '<span class="cpa-share-tag">' + etiq + " " + str(g) + "</span>"
            '<span class="cpa-blocks">' + bloques + "</span>"
            '<span class="cpa-share-get">' + cada_txt + "</span>"
            "</div>"
        )

    cabecera = (
        '<div class="cpa-share-head">'
        + (str(total) + " shared into " + str(grupos) + " equal groups"
           if en else
           str(total) + " repartidos en " + str(grupos) + " grupos iguales")
        + "</div>"
    )
    return ('<div class="cpa-share' + escala + '">'
            + cabecera + "".join(filas) + "</div>")


# -----------------------------------------------------------------------------
# MUNDO 1 — ENIGMAS DE TEXTO
# -----------------------------------------------------------------------------
def explicar_problema(pdata, lang="Español"):
    """El enigma se resuelve en 2 pasos; la pista refuerza la estrategia,
    no el resultado. Aqui lo concreto es la historia misma."""
    total = pdata["p1_ans"]
    correcta = pdata["correcta"]

    if lang == "English":
        s1 = _seccion(
            "1 · UNDERSTAND",
            "Every word problem hides <b>two questions</b>. First find the "
            "<b>total</b>, then apply what happens to it.",
        )
        s2 = _seccion(
            "2 · PICTURE IT",
            f'<div class="cpa-bar">'
            f'<span class="cpa-bar-whole">Total: {total}</span></div>'
            f"Draw the whole first. The second step only changes this bar.",
        )
        s3 = _seccion(
            "3 · SOLVE",
            f"Step 1 gave you <b>{total}</b>. Now read the question again "
            f"and decide: do you <b>add</b>, <b>take away</b> or <b>share</b>?",
        )
        return s1 + s2 + s3 + _resultado("► Answer:", correcta)

    s1 = _seccion(
        "1 · COMPRENDE",
        "Todo enigma esconde <b>dos preguntas</b>. Primero busca el "
        "<b>total</b>, y despues aplica lo que pasa con ese total.",
    )
    s2 = _seccion(
        "2 · DIBÚJALO",
        f'<div class="cpa-bar">'
        f'<span class="cpa-bar-whole">Total: {total}</span></div>'
        f"Dibuja primero el entero. El segundo paso solo modifica esta barra.",
    )
    s3 = _seccion(
        "3 · RESUELVE",
        f"El Paso 1 te dio <b>{total}</b>. Ahora relee la pregunta y decide: "
        f"¿hay que <b>sumar</b>, <b>quitar</b> o <b>repartir</b>?",
    )
    return s1 + s2 + s3 + _resultado("► Respuesta:", correcta)


# -----------------------------------------------------------------------------
# MUNDO 2 — GEOMETRÍA
# -----------------------------------------------------------------------------
def explicar_geometria(gdata, lang="Español"):
    """Perimetro = borde que se recorre. Area = cuadros que se llenan.
    Esa distincion es EL error clasico a esta edad, asi que se dibuja."""
    tipo = gdata["tipo"]
    d = gdata["details"]
    correcta = gdata["correcta"]
    en = lang == "English"

    if tipo == "perimetro_rect":
        a, l = d["ancho"], d["largo"]
        figura = _rect_perimetro(a, l, en)
        if en:
            s1 = _seccion("1 · WHAT IS IT", "The <b>perimeter</b> is the fence "
                          "around the shape. Walk the edge and add every side.")
            s2 = _seccion("2 · PICTURE IT", figura)
            s3 = _seccion("3 · SOLVE",
                          f"{l} + {a} + {l} + {a}<br>"
                          f"or faster: 2 × ({l} + {a}) = 2 × {l + a}")
            return s1 + s2 + s3 + _resultado("► Perimeter:", correcta)
        s1 = _seccion("1 · QUÉ ES", "El <b>perímetro</b> es la reja que rodea "
                      "la figura. Recorre el borde y suma todos los lados.")
        s2 = _seccion("2 · DIBÚJALO", figura)
        s3 = _seccion("3 · RESUELVE",
                      f"{l} + {a} + {l} + {a}<br>"
                      f"o más rápido: 2 × ({l} + {a}) = 2 × {l + a}")
        return s1 + s2 + s3 + _resultado("► Perímetro:", correcta)

    if tipo == "area_grid":
        b, h = d["base"], d["altura"]
        rejilla = _rejilla(h, b, "🟩", en)
        if en:
            s1 = _seccion("1 · WHAT IS IT", "The <b>area</b> is how many "
                          "squares <i>fit inside</i>. Not the border — the filling.")
            s2 = _seccion("2 · PICTURE IT", rejilla)
            s3 = _seccion("3 · SOLVE",
                          f"Count the squares, or multiply:<br>"
                          f"<b>{b} × {h}</b> (base × height)")
            return s1 + s2 + s3 + _resultado("► Area:", correcta)
        s1 = _seccion("1 · QUÉ ES", "El <b>área</b> es cuántos cuadros caben "
                      "<i>adentro</i>. No el borde: el relleno.")
        s2 = _seccion("2 · DIBÚJALO", rejilla)
        s3 = _seccion("3 · RESUELVE",
                      f"Cuenta los cuadros, o multiplica:<br>"
                      f"<b>{b} × {h}</b> (base × altura)")
        return s1 + s2 + s3 + _resultado("► Área:", correcta)

    l1, l2, l3 = d["l1"], d["l2"], d["l3"]
    figura = _triangulo(l1, l2, l3, en)
    if en:
        s1 = _seccion("1 · WHAT IS IT", "The <b>perimeter</b> of a triangle "
                      "is the walk around its 3 sides.")
        s2 = _seccion("2 · PICTURE IT", figura)
        s3 = _seccion("3 · SOLVE", f"{l1} + {l2} + {l3}")
        return s1 + s2 + s3 + _resultado("► Perimeter:", correcta)
    s1 = _seccion("1 · QUÉ ES", "El <b>perímetro</b> de un triángulo es el "
                  "recorrido por sus 3 lados.")
    s2 = _seccion("2 · DIBÚJALO", figura)
    s3 = _seccion("3 · RESUELVE", f"{l1} + {l2} + {l3}")
    return s1 + s2 + s3 + _resultado("► Perímetro:", correcta)


# -----------------------------------------------------------------------------
# MUNDO 3 — ALGORITMOS (multiplicación y división)
# -----------------------------------------------------------------------------
def explicar_operacion(tipo_op, n1, n2, correcta, lang="Español"):
    """Multiplicar = grupos iguales. Dividir = repartir en partes iguales.
    Ambas se dibujan como rejilla; es la misma imagen leida al reves."""
    en = lang == "English"

    if tipo_op == "mult":
        rejilla = _rejilla(n1, n2, en=en)
        if en:
            s1 = _seccion("1 · WHAT IT MEANS",
                          f"<b>{n1} × {n2}</b> means <b>{n1} groups of {n2}</b>.")
            s2 = _seccion("2 · PICTURE IT",
                          rejilla)
            s3 = _seccion("3 · SOLVE",
                          f"Skip-count by {n2}, {n1} times.<br>"
                          f"Or add: {' + '.join([str(n2)] * min(n1, 6))}"
                          + (" + ..." if n1 > 6 else ""))
            return s1 + s2 + s3 + _resultado("► Result:", correcta)
        s1 = _seccion("1 · QUÉ SIGNIFICA",
                      f"<b>{n1} × {n2}</b> significa <b>{n1} grupos de {n2}</b>.")
        s2 = _seccion("2 · DIBÚJALO",
                      rejilla)
        s3 = _seccion("3 · RESUELVE",
                      f"Cuenta de {n2} en {n2}, {n1} veces.<br>"
                      f"O suma: {' + '.join([str(n2)] * min(n1, 6))}"
                      + (" + ..." if n1 > 6 else ""))
        return s1 + s2 + s3 + _resultado("► Resultado:", correcta)

    # Division: n1 / n2 = correcta  -> repartir n1 en n2 grupos
    rejilla = _reparto(n1, n2, correcta, en)
    if en:
        s1 = _seccion("1 · WHAT IT MEANS",
                      f"<b>{n1} ÷ {n2}</b> means sharing <b>{n1}</b> into "
                      f"<b>{n2} equal groups</b>. How many in each group?")
        s2 = _seccion("2 · PICTURE IT",
                      rejilla)
        s3 = _seccion("3 · SOLVE",
                      f"Ask yourself: {n2} × ❓ = {n1}<br>"
                      f"Division is multiplication read backwards.")
        return s1 + s2 + s3 + _resultado("► Result:", correcta)
    s1 = _seccion("1 · QUÉ SIGNIFICA",
                  f"<b>{n1} ÷ {n2}</b> significa repartir <b>{n1}</b> en "
                  f"<b>{n2} grupos iguales</b>. ¿Cuántos van en cada grupo?")
    s2 = _seccion("2 · DIBÚJALO",
                  rejilla)
    s3 = _seccion("3 · RESUELVE",
                  f"Pregúntate: {n2} × ❓ = {n1}<br>"
                  f"Dividir es multiplicar al revés.")
    return s1 + s2 + s3 + _resultado("► Resultado:", correcta)


# -----------------------------------------------------------------------------
# MUNDO 4 — FRACCIONES
# -----------------------------------------------------------------------------
def explicar_fraccion(num, den, lang="Español"):
    """El error clasico: contar las partes pintadas pero no ver que el
    denominador es el TOTAL de partes iguales. Se dibuja la barra completa."""
    en = lang == "English"

    barra = (
        '<div class="cpa-frac-bar">'
        + "".join('<span class="cpa-frac-on"></span>' for _ in range(num))
        + "".join('<span class="cpa-frac-off"></span>' for _ in range(den - num))
        + "</div>"
        + f'<div class="cpa-frac-legend">'
        f'<span class="cpa-frac-on"></span> {num} '
        f'{"painted" if en else "pintadas"} &nbsp;·&nbsp; '
        f'{den} {"equal parts in total" if en else "partes iguales en total"}'
        f"</div>"
    )

    if en:
        s1 = _seccion("1 · WHAT IT MEANS",
                      "A fraction splits <b>one whole</b> into equal parts. "
                      "The bottom number says <i>how many parts</i>, the top "
                      "says <i>how many we take</i>.")
        s2 = _seccion("2 · PICTURE IT", barra)
        s3 = _seccion("3 · SOLVE",
                      f'<div class="cpa-frac-math">'
                      f'<span class="cpa-num">{num}</span>'
                      f'<span class="cpa-line"></span>'
                      f'<span class="cpa-den">{den}</span>'
                      f'</div>'
                      f"<b>{num}</b> = numerator (painted)<br>"
                      f"<b>{den}</b> = denominator (total parts)")
        return s1 + s2 + s3 + _resultado("► Fraction:", f"{num}/{den}")

    s1 = _seccion("1 · QUÉ SIGNIFICA",
                  "Una fracción parte <b>un entero</b> en trozos iguales. "
                  "El número de abajo dice <i>en cuántas partes</i>, el de "
                  "arriba dice <i>cuántas tomamos</i>.")
    s2 = _seccion("2 · DIBÚJALO", barra)
    s3 = _seccion("3 · RESUELVE",
                  f'<div class="cpa-frac-math">'
                  f'<span class="cpa-num">{num}</span>'
                  f'<span class="cpa-line"></span>'
                  f'<span class="cpa-den">{den}</span>'
                  f'</div>'
                  f"<b>{num}</b> = numerador (las pintadas)<br>"
                  f"<b>{den}</b> = denominador (total de partes)")
    return s1 + s2 + s3 + _resultado("► Fracción:", f"{num}/{den}")


# -----------------------------------------------------------------------------
# MUNDO 5 — DECIMALES
# -----------------------------------------------------------------------------
def explicar_decimal(tipo, d_data, correcta, lang="Español"):
    """Los 3 ejercicios atacan conceptos distintos: valor posicional,
    comparacion y conversion. Cada uno necesita su propia imagen."""
    en = lang == "English"

    if tipo == 1:
        e, d, c = d_data["e"], d_data["d"], d_data["c"]
        tabla = (
            '<div class="cpa-place">'
            f'<div><span class="cpa-place-h">{"Units" if en else "Enteros"}</span>'
            f'<span class="cpa-place-v">{e}</span></div>'
            f'<div class="cpa-place-dot">,</div>'
            f'<div><span class="cpa-place-h">{"Tenths" if en else "Décimas"}</span>'
            f'<span class="cpa-place-v">{d}</span></div>'
            f'<div><span class="cpa-place-h">{"Hundredths" if en else "Centésimas"}</span>'
            f'<span class="cpa-place-v">{c}</span></div>'
            "</div>"
        )
        if en:
            s1 = _seccion("1 · WHAT IT MEANS",
                          "Each position after the comma is <b>10 times "
                          "smaller</b>. Tenths first, then hundredths.")
            s2 = _seccion("2 · PICTURE IT", tabla)
            s3 = _seccion("3 · SOLVE",
                          f"{e} whole + {d} tenths + {c} hundredths<br>"
                          f"= {e} + 0.{d} + 0.0{c}")
            return s1 + s2 + s3 + _resultado("► Decimal:", correcta)
        s1 = _seccion("1 · QUÉ SIGNIFICA",
                      "Cada posición después de la coma es <b>10 veces más "
                      "pequeña</b>. Primero las décimas, luego las centésimas.")
        s2 = _seccion("2 · DIBÚJALO", tabla)
        s3 = _seccion("3 · RESUELVE",
                      f"{e} entero + {d} décimas + {c} centésimas<br>"
                      f"= {e} + 0,{d} + 0,0{c}")
        return s1 + s2 + s3 + _resultado("► Decimal:", correcta)

    if tipo == 2:
        nA, nB = d_data["nA"], d_data["nB"]
        comp = (
            f'<div class="cpa-compare">'
            f'<div class="cpa-comp-item"><b>A</b><span>{nA}</span></div>'
            f'<div class="cpa-comp-vs">vs</div>'
            f'<div class="cpa-comp-item"><b>B</b><span>{nB}</span></div>'
            f"</div>"
        )
        if en:
            s1 = _seccion("1 · WHAT IT MEANS",
                          "To compare decimals, look at the <b>tenths first</b>, "
                          "then the hundredths. More digits does <i>not</i> mean bigger.")
            s2 = _seccion("2 · PICTURE IT", comp)
            s3 = _seccion("3 · SOLVE",
                          "Line up the commas and compare column by column, "
                          "left to right — like reading a word.")
            return s1 + s2 + s3 + _resultado("► Greater:", f"{correcta}")
        s1 = _seccion("1 · QUÉ SIGNIFICA",
                      "Para comparar decimales mira <b>primero las décimas</b>, "
                      "luego las centésimas. Más cifras <i>no</i> significa mayor.")
        s2 = _seccion("2 · DIBÚJALO", comp)
        s3 = _seccion("3 · RESUELVE",
                      "Alinea las comas y compara columna por columna, de "
                      "izquierda a derecha — como si leyeras una palabra.")
        return s1 + s2 + s3 + _resultado("► Mayor:", f"{correcta}")

    num_f, den_f = d_data["num_f"], d_data["den_f"]
    pos = "tenths" if den_f == 10 else "hundredths"
    pos_es = "décimas" if den_f == 10 else "centésimas"
    if en:
        s1 = _seccion("1 · WHAT IT MEANS",
                      f"Dividing by {den_f} moves every digit "
                      f"<b>{1 if den_f == 10 else 2} place(s) to the right</b>.")
        s2 = _seccion("2 · PICTURE IT",
                      f'<div class="cpa-convert">'
                      f'<span>{num_f}/{den_f}</span> ➜ '
                      f'<span>{num_f} {pos}</span> ➜ '
                      f'<span class="cpa-convert-out">{correcta}</span></div>')
        s3 = _seccion("3 · SOLVE",
                      f"{num_f} ÷ {den_f} — the comma jumps "
                      f"{1 if den_f == 10 else 2} step(s) left.")
        return s1 + s2 + s3 + _resultado("► Decimal:", correcta)
    s1 = _seccion("1 · QUÉ SIGNIFICA",
                  f"Dividir entre {den_f} corre cada cifra "
                  f"<b>{1 if den_f == 10 else 2} lugar(es) a la derecha</b>.")
    s2 = _seccion("2 · DIBÚJALO",
                  f'<div class="cpa-convert">'
                  f'<span>{num_f}/{den_f}</span> ➜ '
                  f'<span>{num_f} {pos_es}</span> ➜ '
                  f'<span class="cpa-convert-out">{correcta}</span></div>')
    s3 = _seccion("3 · RESUELVE",
                  f"{num_f} ÷ {den_f} — la coma salta "
                  f"{1 if den_f == 10 else 2} paso(s) a la izquierda.")
    return s1 + s2 + s3 + _resultado("► Decimal:", correcta)
