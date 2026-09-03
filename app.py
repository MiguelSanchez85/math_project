import base64
from datetime import datetime
import random
import time
import pandas as pd
import streamlit as st

from ui import cargar_estilos

# Intenta importar la conexión de Google Sheets
try:
    from streamlit_gsheets import GSheetsConnection
    HAS_GSHEETS = True
except ImportError:
    HAS_GSHEETS = False


def cargar_imagen_base64(ruta_imagen):
    """Lee una imagen local y la convierte a string Base64 para usar directo en HTML."""
    try:
        with open(ruta_imagen, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            return f"data:image/png;base64,{encoded}"
    except FileNotFoundError:
        return None


# Carga de recursos locales
AVATAR_ESCOLAR_BASE64 = cargar_imagen_base64("avatar_base.png")
LOGO_COLEGIO_BASE64 = cargar_imagen_base64("logo_colegio.png")

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Math Quest: Guardianes del Número",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. HOJA DE ESTILOS (ver style.css / DESIGN_NOTES.md)
# -----------------------------------------------------------------------------
cargar_estilos()

# -----------------------------------------------------------------------------
# 3. GENERADORES DINÁMICOS BILINGÜES MULTI-IDIOMA
# -----------------------------------------------------------------------------

def nuevo_reto_problemas_texto(idioma="Español"):
    if idioma == "English":
        personajes = ["Lucas", "Sophia", "Matthew", "Emma", "Leo", "Camila", "Ethan", "Isabella"]
        objetos = [
            ("supply crates", "energy cookies"),
            ("gem chests", "mystic crystals"),
            ("sticker packs", "legendary cards"),
            ("bags of apples", "magic fruits")
        ]
        p = random.choice(personajes)
        contenedor, ítem = random.choice(objetos)
        tipo = random.choice([1, 2, 3])

        if tipo == 1:
            cant_c = random.randint(3, 8)
            cant_p = random.randint(4, 9)
            regalo = random.randint(2, min(10, cant_c * cant_p - 1))
            total_i = cant_c * cant_p
            correcta = total_i - regalo
            historia = f"**{p}** has **{cant_c} {contenedor}**. Each one contains **{cant_p} {ítem}**. If {p} gives **{regalo} {ítem}** to a teammate, how many are left in total?"
            p1_q = f"How many {ítem} did {p} have in total before giving any away?"
            p2_q = f"If there were {total_i} and {regalo} were given away, how many are left?"
        elif tipo == 2:
            cant1, cant2 = random.randint(10, 30), random.randint(10, 30)
            amigos = random.choice([2, 3, 4, 5])
            tot = cant1 + cant2
            tot_ajustado = tot + (amigos - (tot % amigos)) if tot % amigos != 0 else tot
            cant2 = tot_ajustado - cant1
            correcta = tot_ajustado // amigos
            historia = f"**{p}** collected **{cant1} {ítem}** on Monday and **{cant2} {ítem}** on Tuesday. Then shared them equally among **{amigos} friends**. How many does each friend get?"
            p1_q = f"How many {ítem} were collected in total across both days?"
            p2_q = f"If {tot_ajustado} are split equally among {amigos} friends, how many does each receive?"
            total_i = tot_ajustado
        else:
            paquetes, unidades, guardados = random.randint(2, 6), random.randint(5, 10), random.randint(5, 20)
            total_i = paquetes * unidades
            correcta = total_i + guardados
            historia = f"**{p}** bought **{paquetes} {contenedor}** with **{unidades} {ítem}** each. If {p} already had **{guardados} {ítem}** in the backpack, how many are there in total?"
            p1_q = f"How many {ítem} were bought in the new packages?"
            p2_q = f"If {total_i} were bought and {guardados} were already saved, how many are there in total?"

    else: # Español
        personajes = ["Lucas", "Valentina", "Mateo", "Sofía", "Leo", "Camila", "Tomás", "Isabella"]
        objetos = [
            ("cajas de suministros", "galletas de energía", "las", "cuántas"),
            ("cofres de gemas", "cristales marea", "los", "cuántos"),
            ("sobres de cartas", "cartas legendarias", "las", "cuántas"),
            ("bolsas de manzanas", "frutas mágicas", "las", "cuántas")
        ]
        p = random.choice(personajes)
        contenedor, ítem, art, cant_preg = random.choice(objetos)
        tipo = random.choice([1, 2, 3])

        if tipo == 1:
            cant_c = random.randint(3, 8)
            cant_p = random.randint(4, 9)
            regalo = random.randint(2, min(10, cant_c * cant_p - 1))
            total_i = cant_c * cant_p
            correcta = total_i - regalo
            historia = f"**{p}** tiene **{cant_c} {contenedor}**. Cada una contiene **{cant_p} {ítem}**. Si decide regalar **{regalo} {ítem}** a su compañero de equipo, ¿cuántas le quedan en total?" if art == "las" else f"**{p}** tiene **{cant_c} {contenedor}**. Cada uno contiene **{cant_p} {ítem}**. Si decide regalar **{regalo} {ítem}** a su compañero de equipo, ¿cuántos le quedan en total?"
            p1_q = f"¿{cant_preg.capitalize()} {ítem} tenía en total antes de regalar?"
            p2_q = f"Si tenía {total_i} y regaló {regalo}, ¿{cant_preg} le quedan?"
        elif tipo == 2:
            cant1, cant2 = random.randint(10, 30), random.randint(10, 30)
            amigos = random.choice([2, 3, 4, 5])
            tot = cant1 + cant2
            tot_ajustado = tot + (amigos - (tot % amigos)) if tot % amigos != 0 else tot
            cant2 = tot_ajustado - cant1
            correcta = tot_ajustado // amigos
            historia = f"**{p}** recolectó **{cant1} {ítem}** el lunes y **{cant2} {ítem}** el martes. Luego {art} repartió en partes iguales entre sus **{amigos} amigos**. ¿{cant_preg.capitalize()} le tocan a cada uno?"
            p1_q = f"¿{cant_preg.capitalize()} {ítem} recolectó en total entre los dos días?"
            p2_q = f"Si reparte {tot_ajustado} entre {amigos} amigos, ¿{cant_preg} recibe cada uno?"
            total_i = tot_ajustado
        else:
            paquetes, unidades, guardados = random.randint(2, 6), random.randint(5, 10), random.randint(5, 20)
            total_i = paquetes * unidades
            correcta = total_i + guardados
            historia = f"**{p}** compró **{paquetes} {contenedor}** con **{unidades} {ítem}** cada uno. Si ya tenía **{guardados} {ítem}** guardados en su mochila, ¿{cant_preg} tiene ahora en total?"
            p1_q = f"¿{cant_preg.capitalize()} {ítem} compró en los paquetes nuevos?"
            p2_q = f"Si compró {total_i} y ya tenía {guardados}, ¿{cant_preg} tiene en total?"

    p2_opciones = list(set([correcta, correcta + 2, max(1, correcta - 2), total_i]))
    random.shuffle(p2_opciones)
    st.session_state.prob_data = {
        "historia": historia, "p1_q": p1_q, "p1_ans": total_i,
        "p2_q": p2_q, "correcta": correcta, "p2_opciones": p2_opciones
    }
    st.session_state.mostrar_pista_prob = False
    st.session_state.reto_prob_id = time.time()


def nuevo_reto_geometria(idioma="Español"):
    tipo = random.choice(["perimetro_rect", "area_grid", "perimetro_triang"])
    
    if tipo == "perimetro_rect":
        ancho, largo = random.randint(3, 10), random.randint(4, 12)
        correcta = 2 * (ancho + largo)
        distractoras = [ancho + largo, ancho * largo, correcta + 2, max(4, correcta - 4)]
        data = {"ancho": ancho, "largo": largo, "tipo": tipo}
    elif tipo == "area_grid":
        base, altura = random.randint(2, 6), random.randint(2, 5)
        correcta = base * altura
        distractoras = [base + altura, 2 * (base + altura), correcta + 3, max(2, correcta - 2)]
        data = {"base": base, "altura": altura, "tipo": tipo}
    else:
        l1, l2, l3 = random.randint(4, 10), random.randint(4, 10), random.randint(4, 10)
        correcta = l1 + l2 + l3
        distractoras = [l1 + l2, correcta + 2, max(3, correcta - 3)]
        data = {"l1": l1, "l2": l2, "l3": l3, "tipo": tipo}

    opciones = list(set([correcta] + distractoras))
    random.shuffle(opciones)
    st.session_state.geom_data = {"tipo": tipo, "correcta": correcta, "opciones": opciones, "details": data}
    st.session_state.mostrar_pista_geom = False
    st.session_state.reto_geom_id = time.time()


def nuevo_reto_operaciones(idioma="Español"):
    st.session_state.tipo_operacion = random.choice(["mult", "div"])
    if st.session_state.tipo_operacion == "mult":
        st.session_state.num1 = random.randint(2, 9)
        st.session_state.num2 = random.randint(1, 10)
        st.session_state.correcta_op = st.session_state.num1 * st.session_state.num2
    else:
        divisor = random.randint(2, 8)
        resultado = random.randint(1, 10)
        st.session_state.num1 = divisor * resultado
        st.session_state.num2 = divisor
        st.session_state.correcta_op = resultado

    st.session_state.mostrar_pista_op = False
    st.session_state.reto_op_id = time.time()


def nuevo_reto_fracciones():
    den = random.choice([2, 3, 4, 5, 6, 8, 10])
    num = random.randint(1, den - 1)
    st.session_state.denominador = den
    st.session_state.numerador = num
    st.session_state.mostrar_pista_frac = False
    st.session_state.reto_frac_id = time.time()


def nuevo_reto_decimales():
    tipo = random.choice([1, 2, 3])
    st.session_state.tipo_ejercicio_dec = tipo
    st.session_state.mostrar_pista_dec = False
    st.session_state.reto_dec_id = time.time()

    if tipo == 1:
        e, d, c = random.randint(0, 5), random.randint(1, 9), random.randint(0, 9)
        val_real = round(e + d / 10 + c / 100, 2)
        st.session_state.dec_data = {"e": e, "d": d, "c": c}
        correcta = str(val_real)
        distractoras = [str(round(val_real + 0.1, 2)), str(round(val_real - 0.01 if val_real > 0.01 else 0.05, 2)), f"{e}.{c}{d}"]
        opciones = list(set([correcta] + distractoras))
        random.shuffle(opciones)
        st.session_state.dec_correcta = correcta
        st.session_state.dec_opciones = opciones
    elif tipo == 2:
        base = round(random.uniform(0.1, 9.9), 1)
        diferencia = random.choice([0.01, 0.05, 0.1, 0.15])
        nA, nB = round(base, 2), round(base + diferencia, 2)
        if random.choice([True, False]): nA, nB = nB, nA
        st.session_state.dec_data = {"nA": nA, "nB": nB}
        st.session_state.dec_correcta = "A" if nA > nB else "B"
        st.session_state.dec_opciones = ["A", "B"]
    else:
        num_f = random.choice([3, 7, 12, 45, 8, 25, 64, 89])
        den_f = random.choice([10, 100])
        val_real = round(num_f / den_f, 2)
        st.session_state.dec_data = {"num_f": num_f, "den_f": den_f}
        correcta = str(val_real)
        distractoras = [str(round(val_real * 10, 2)), str(round(val_real / 10, 2))]
        opciones = list(set([correcta] + distractoras))
        random.shuffle(opciones)
        st.session_state.dec_correcta = correcta
        st.session_state.dec_opciones = opciones


# -----------------------------------------------------------------------------
# 4. RENDERIZADOR AVATAR
# -----------------------------------------------------------------------------
def renderizar_avatar_dinamico(img_base, img_casco=None, img_escudo=None, img_mascota=None, size=80):
    capas = f'<img src="{img_base}" style="position:absolute; top:2%; left:2%; width:96%; height:96%; object-fit:contain; z-index:2;" />'
    if img_casco:
        capas += f'<img src="{img_casco}" style="position:absolute; top:-20%; left:15%; width:70%; height:50%; object-fit:contain; z-index:4;" />'
    if img_escudo:
        capas += f'<img src="{img_escudo}" style="position:absolute; bottom:5%; right:-10%; width:40%; height:40%; object-fit:contain; z-index:5;" />'
    if img_mascota:
        capas += f'<img src="{img_mascota}" style="position:absolute; bottom:0%; left:-15%; width:40%; height:40%; object-fit:contain; z-index:3;" />'

    return f'<div style="position:relative; width:{size}px; height:{size}px; display:inline-block; vertical-align:middle; background:#f1f5f9; border-radius:50%; border:3px solid #cbd5e1; flex-shrink:0;">{capas}</div>'

# -----------------------------------------------------------------------------
# 5. DICCIONARIOS Y NAVEGACIÓN BILINGÜE
# -----------------------------------------------------------------------------
with st.sidebar:
    if LOGO_COLEGIO_BASE64:
        st.markdown(f'<div class="logo-container"><img src="{LOGO_COLEGIO_BASE64}" class="logo-img" /></div>', unsafe_allow_html=True)
    
    st.title("⚙️ Ajustes / Settings")
    lang_prev = st.session_state.get("lang_actual", "Español")
    lang = st.radio("🌐 Idioma / Language:", options=["Español", "English"], index=0)
    
    if lang != lang_prev:
        st.session_state.lang_actual = lang
        nuevo_reto_problemas_texto(lang)
        nuevo_reto_geometria(lang)
        nuevo_reto_operaciones(lang)
        st.rerun()

TEXTS = {
    "Español": {
        "title": "🛡️ Math Quest: Guardianes del Número",
        "welcome": "¡Bienvenido, Pequeño Guardián!",
        "input_label": "Ingresa tu Nombre o Código de Estudiante:",
        "select_hero": "Elige tu Héroe Base:",
        "btn_start": "¡Comenzar Aventura! 🚀",
        "level": "Nivel",
        "tab_prob": "📜 Enigmas",
        "tab_geom": "📐 Geometría",
        "tab_op": "🌲 Algoritmos",
        "tab_frac": "🍕 Fracciones",
        "tab_dec": "💎 Decimales",
        "tab_shop": "🛒 Tienda",
        "cpa_title": "💡 Pista Conceptual (Explicación CPA)",
        "correct_answer_label": "Resultado Correcto:",
        "correct": "¡Excelente Trabajo! +10 Gemas 🎉",
        "incorrect": "¡Casi! Lee la pista arriba y vuelve a intentarlo.",
        "shop_caption": "🛒 **Tienda del Guardián:** Personaliza tu personaje con tus gemas.",
        "buy": "Comprar", "equip": "✨ Equipar", "unequip": "❌ Desequipar", "no_gems": "¡Gemas insuficientes!",
        "step1_title": "Paso 1: Análisis Inicial",
        "step2_title": "Paso 2: Solución Final",
        "p1_correct": "¡Paso 1 Correcto! 🎯 Ahora resuelve el paso final.",
        "p1_wrong": "Revisa tus cálculos del Paso 1 antes de continuar.",
        "p1_input_label": "Tu respuesta del Paso 1:",
        "op_question": "¿Cuánto es",
        "crystal_prefix": "Cristal",
        "dec_q1": "¿Qué decimal representa?",
        "dec_q2": "¿Cuál cristal es MAYOR?",
        "dec_q3": "Convierte a decimal:"
    },
    "English": {
        "title": "🛡️ Math Quest: Number Guardians",
        "welcome": "Welcome, Little Guardian!",
        "input_label": "Enter your Name or Student ID:",
        "select_hero": "Choose your Base Hero:",
        "btn_start": "Start Adventure! 🚀",
        "level": "Level",
        "tab_prob": "📜 Word Quests",
        "tab_geom": "📐 Geometry",
        "tab_op": "🌲 Algorithms",
        "tab_frac": "🍕 Fractions",
        "tab_dec": "💎 Decimals",
        "tab_shop": "🛒 Shop",
        "cpa_title": "💡 Conceptual Hint (CPA Explanation)",
        "correct_answer_label": "Correct Answer:",
        "correct": "Awesome Job! +10 Gems 🎉",
        "incorrect": "Almost! Check the hint above and try again.",
        "shop_caption": "🛒 **Guardian Shop:** Use your gems to customize your hero.",
        "buy": "Buy", "equip": "✨ Equip", "unequip": "❌ Unequip", "no_gems": "Not enough gems!",
        "step1_title": "Step 1: Initial Analysis",
        "step2_title": "Step 2: Final Solution",
        "p1_correct": "Step 1 Correct! 🎯 Now solve the final step.",
        "p1_wrong": "Double check Step 1 calculations before going on.",
        "p1_input_label": "Your Step 1 answer:",
        "op_question": "How much is",
        "crystal_prefix": "Crystal",
        "dec_q1": "Which decimal does this represent?",
        "dec_q2": "Which crystal is GREATER?",
        "dec_q3": "Convert to decimal:"
    },
}

t = TEXTS[lang]

CDN_BASE = "https://openmoji.org/data/color/svg"
PERSONAJES_BASE = {
    "guardian_escolar": {"nombre": "Isabelino", "img": AVATAR_ESCOLAR_BASE64},
    "mago": {"nombre": "Mago / Wizard", "img": f"{CDN_BASE}/1F9D9.svg"},
    "guardiana": {"nombre": "Guardiana / Ranger", "img": f"{CDN_BASE}/1F9DC.svg"},
    "bot": {"nombre": "Cyber-Bot 3000", "img": f"{CDN_BASE}/1F916.svg"},
    "guerrero": {"nombre": "Guerrero / Knight", "img": f"{CDN_BASE}/1F977.svg"},
}

TIENDA_ITEMS = {
    "sombrero_mago": {"nombre": "Magic Hat" if lang == "English" else "Sombrero Mágico", "img": f"{CDN_BASE}/1F3A9.svg", "precio": 30, "tipo": "Casco"},
    "corona_real": {"nombre": "Wisdom Crown" if lang == "English" else "Corona de Sabiduría", "img": f"{CDN_BASE}/1F451.svg", "precio": 60, "tipo": "Casco"},
    "dragonsito": {"nombre": "Fire Dragon" if lang == "English" else "Dragón de Fuego", "img": f"{CDN_BASE}/1F409.svg", "precio": 80, "tipo": "Mascota"},
    "gato_sabio": {"nombre": "Astro Cat" if lang == "English" else "Gato Astro", "img": f"{CDN_BASE}/1F431.svg", "precio": 40, "tipo": "Mascota"},
    "escudo_estelar": {"nombre": "Cosmic Shield" if lang == "English" else "Escudo Cósmico", "img": f"{CDN_BASE}/1F6E1.svg", "precio": 50, "tipo": "Escudo"},
}

# Inicialización de Estados
if "prob_data" not in st.session_state: nuevo_reto_problemas_texto(lang)
if "geom_data" not in st.session_state: nuevo_reto_geometria(lang)
if "tipo_operacion" not in st.session_state: nuevo_reto_operaciones(lang)
if "numerador" not in st.session_state: nuevo_reto_fracciones()
if "tipo_ejercicio_dec" not in st.session_state: nuevo_reto_decimales()
if "gemas" not in st.session_state: st.session_state.gemas = 0
if "nivel" not in st.session_state: st.session_state.nivel = 1
if "equipado" not in st.session_state: st.session_state.equipado = {"Casco": None, "Mascota": None, "Escudo": None}

def sincronizar_progreso(estudiante_id, nombre, gemas, nivel):
    if not HAS_GSHEETS: return
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Estudiantes", ttl=0)
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if estudiante_id in df["ID_Estudiante"].astype(str).values:
            df.loc[df["ID_Estudiante"].astype(str) == estudiante_id, ["Gemas", "Nivel", "Ultimo_Acceso"]] = [gemas, nivel, ahora]
        else:
            nuevo = pd.DataFrame([{"ID_Estudiante": estudiante_id, "Nombre": nombre, "Gemas": gemas, "Nivel": nivel, "Ultimo_Acceso": ahora}])
            df = pd.concat([df, nuevo], ignore_index=True)
        conn.update(worksheet="Estudiantes", data=df)
    except Exception: pass

# -----------------------------------------------------------------------------
# 6. LOGIN Y PANTALLA PRINCIPAL
# -----------------------------------------------------------------------------
if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = False

if not st.session_state.usuario_activo:
    st.title(t["title"])
    st.subheader(t["welcome"])
    with st.form("form_login"):
        nombre_input = st.text_input(t["input_label"])
        personaje_sel = st.selectbox(t["select_hero"], options=list(PERSONAJES_BASE.keys()), format_func=lambda x: PERSONAJES_BASE[x]["nombre"])
        if st.form_submit_button(t["btn_start"], use_container_width=True) and nombre_input.strip():
            st.session_state.estudiante_id = nombre_input.strip().lower().replace(" ", "_")
            st.session_state.estudiante_nombre = nombre_input.strip()
            st.session_state.personaje_base = personaje_sel
            st.session_state.gemas = 100
            st.session_state.nivel = 1
            st.session_state.inventario = []
            st.session_state.usuario_activo = True
            st.rerun()
    st.stop()

# HUD Bar Rediseñada
hero_base = st.session_state.get("personaje_base", "mago")
img_b = PERSONAJES_BASE[hero_base]["img"]
c_id, m_id, e_id = st.session_state.equipado.get("Casco"), st.session_state.equipado.get("Mascota"), st.session_state.equipado.get("Escudo")

avatar_html = renderizar_avatar_dinamico(
    img_b,
    TIENDA_ITEMS[c_id]["img"] if c_id else None,
    TIENDA_ITEMS[e_id]["img"] if e_id else None,
    TIENDA_ITEMS[m_id]["img"] if m_id else None
)

c1, c2, c3 = st.columns([2.5, 1, 1])
with c1:
    st.markdown(f'<div style="display:flex; align-items:center; gap:12px;">{avatar_html}<span style="font-size:22px; font-weight:800; color:#0f172a;">{st.session_state.estudiante_nombre}</span></div>', unsafe_allow_html=True)
with c2: st.markdown(f"### 💎 `{st.session_state.gemas}`")
with c3: st.markdown(f"### ⭐ {t['level']} `{st.session_state.nivel}`")

st.divider()

# -----------------------------------------------------------------------------
# 7. MUNDOS Y ACTIVIDADES DE APRENDIZAJE
# -----------------------------------------------------------------------------
tab_prob, tab_geom, tab_op, tab_frac, tab_dec, tab_tienda = st.tabs(
    [t["tab_prob"], t["tab_geom"], t["tab_op"], t["tab_frac"], t["tab_dec"], t["tab_shop"]]
)

# === MUNDO 1: ENIGMAS DE TEXTO ===
with tab_prob:
    pdata = st.session_state.prob_data
    st.markdown(f'''
        <div class="question-card">
            <div class="question-badge">{t["tab_prob"]}</div><br>
            {pdata["historia"]}
        </div>
    ''', unsafe_allow_html=True)
    
    st.subheader(t["step1_title"])
    st.write(f"👉 **{pdata['p1_q']}**")
    p1_input = st.number_input(t["p1_input_label"], min_value=0, value=0, step=1, key=f"p1_{st.session_state.reto_prob_id}")
    
    if p1_input == pdata["p1_ans"]:
        st.success(t["p1_correct"])
        st.subheader(t["step2_title"])
        st.write(f"🎯 **{pdata['p2_q']}**")
        
        cols = st.columns(2)
        for idx, opt in enumerate(pdata["p2_opciones"]):
            with cols[idx % 2]:
                if st.button(f"✨ {opt}", key=f"btn_p_{st.session_state.reto_prob_id}_{idx}_{opt}", use_container_width=True):
                    if opt == pdata["correcta"]:
                        st.balloons()
                        st.success(t["correct"])
                        st.session_state.gemas += 10
                        if st.session_state.gemas % 50 == 0: st.session_state.nivel += 1
                        sincronizar_progreso(st.session_state.estudiante_id, st.session_state.estudiante_nombre, st.session_state.gemas, st.session_state.nivel)
                        time.sleep(0.5)
                        nuevo_reto_problemas_texto(lang)
                        st.rerun()
                    else:
                        st.session_state.mostrar_pista_prob = True
                        st.error(t["incorrect"])
                        st.rerun()
    elif p1_input > 0:
        st.warning(t["p1_wrong"])

    if st.session_state.mostrar_pista_prob:
        st.markdown(f'<div class="cpa-box"><b>{t["cpa_title"]}</b><br>• {t["correct_answer_label"]} <b>{pdata["correcta"]}</b></div>', unsafe_allow_html=True)

# === MUNDO 2: GEOMETRÍA ===
with tab_geom:
    gdata = st.session_state.geom_data
    d = gdata["details"]
    
    if lang == "English":
        if gdata["tipo"] == "perimetro_rect":
            prompt = f"Calculate the <span class='highlight-text'>PERIMETER</span>.<br><b>Width:</b> {d['ancho']} m | <b>Length:</b> {d['largo']} m"
            pista = "Perimeter = Sum of all 4 sides."
        elif gdata["tipo"] == "area_grid":
            prompt = f"Calculate the <span class='highlight-text'>AREA</span>.<br><b>Base:</b> {d['base']} blocks | <b>Height:</b> {d['altura']} blocks"
            pista = "Area = Multiply Base × Height."
        else:
            prompt = f"Calculate the <span class='highlight-text'>PERIMETER</span>.<br><b>Sides:</b> {d['l1']} cm, {d['l2']} cm, {d['l3']} cm"
            pista = "Perimeter = Sum of the 3 sides."
    else:
        if gdata["tipo"] == "perimetro_rect":
            prompt = f"Calcula el <span class='highlight-text'>PERÍMETRO</span>.<br><b>Ancho:</b> {d['ancho']} m | <b>Largo:</b> {d['largo']} m"
            pista = "El Perímetro es la suma de los 4 lados."
        elif gdata["tipo"] == "area_grid":
            prompt = f"Calcula el <span class='highlight-text'>ÁREA</span>.<br><b>Base:</b> {d['base']} bloques | <b>Altura:</b> {d['altura']} bloques"
            pista = "El Área es el total de cuadros: Multiplica Base × Altura."
        else:
            prompt = f"Calcula el <span class='highlight-text'>PERÍMETRO</span>.<br><b>Lados:</b> {d['l1']} cm, {d['l2']} cm, {d['l3']} cm"
            pista = "El Perímetro es la suma de los 3 lados."

    st.markdown(f'<div class="question-card"><div class="question-badge">{t["tab_geom"]}</div><br>{prompt}</div>', unsafe_allow_html=True)

    if st.session_state.mostrar_pista_geom:
        st.markdown(f'<div class="cpa-box"><b>{t["cpa_title"]}</b><br>• {pista}<br>• {t["correct_answer_label"]} <b>{gdata["correcta"]}</b></div>', unsafe_allow_html=True)

    g_cols = st.columns(2)
    for idx, opt in enumerate(gdata["opciones"]):
        with g_cols[idx % 2]:
            if st.button(f"📐 {opt}", key=f"btn_g_{st.session_state.reto_geom_id}_{idx}_{opt}", use_container_width=True):
                if opt == gdata["correcta"]:
                    st.balloons()
                    st.success(t["correct"])
                    st.session_state.gemas += 10
                    if st.session_state.gemas % 50 == 0: st.session_state.nivel += 1
                    sincronizar_progreso(st.session_state.estudiante_id, st.session_state.estudiante_nombre, st.session_state.gemas, st.session_state.nivel)
                    time.sleep(0.5)
                    nuevo_reto_geometria(lang)
                    st.rerun()
                else:
                    st.session_state.mostrar_pista_geom = True
                    st.error(t["incorrect"])
                    st.rerun()

# === MUNDO 3: ALGORITMOS Y OPERACIONES ===
with tab_op:
    tipo_op = st.session_state.tipo_operacion
    n1, n2 = st.session_state.num1, st.session_state.num2
    correcta_o = st.session_state.correcta_op

    q_sym = "×" if tipo_op == "mult" else "÷"
    st.markdown(f'<div class="question-card"><div class="question-badge">{t["tab_op"]}</div><br>{t["op_question"]} <span class="highlight-text">{n1} {q_sym} {n2}</span>?</div>', unsafe_allow_html=True)

    if st.session_state.mostrar_pista_op:
        st.markdown(f'<div class="cpa-box"><b>{t["cpa_title"]}</b><br>• {t["correct_answer_label"]} <b>{correcta_o}</b></div>', unsafe_allow_html=True)

    opciones_o = list({correcta_o, correcta_o + 2, max(1, correcta_o - 1), correcta_o + 3})
    random.shuffle(opciones_o)

    g1, g2 = st.columns(2)
    for idx, opt in enumerate(opciones_o):
        with (g1 if idx % 2 == 0 else g2):
            if st.button(f"⚡ {opt}", key=f"btn_o_{st.session_state.reto_op_id}_{idx}_{opt}", use_container_width=True):
                if opt == correcta_o:
                    st.balloons()
                    st.success(t["correct"])
                    st.session_state.gemas += 10
                    if st.session_state.gemas % 50 == 0: st.session_state.nivel += 1
                    sincronizar_progreso(st.session_state.estudiante_id, st.session_state.estudiante_nombre, st.session_state.gemas, st.session_state.nivel)
                    time.sleep(0.5)
                    nuevo_reto_operaciones(lang)
                    st.rerun()
                else:
                    st.session_state.mostrar_pista_op = True
                    st.error(t["incorrect"])
                    st.rerun()

# === MUNDO 4: FRACCIONES ===
with tab_frac:
    num, den = st.session_state.numerador, st.session_state.denominador
    bloques = "🟩 " * num + "⬜ " * (den - num)
    q_txt = "Which fraction represents this bar?" if lang == "English" else "¿Qué fracción representa esta barra?"
    st.markdown(f'<div class="question-card"><div class="question-badge">{t["tab_frac"]}</div><br>{q_txt}<div class="fraction-visual">{bloques}</div></div>', unsafe_allow_html=True)
    correcta_f = f"{num}/{den}"
    distractoras = [f"{den - num}/{den}", f"{num}/{den + 1 if den < 8 else den - 1}"]

    if st.session_state.mostrar_pista_frac:
        st.markdown(f'<div class="cpa-box"><b>{t["cpa_title"]}</b><br>• Numerator = {num} / Denominator = {den}' if lang == "English" else f'<div class="cpa-box"><b>{t["cpa_title"]}</b><br>• Numerador = {num} / Denominador = {den}</div>', unsafe_allow_html=True)

    opciones_f = list(set([correcta_f] + distractoras))
    random.shuffle(opciones_f)

    gf1, gf2 = st.columns(2)
    for idx, opt in enumerate(opciones_f):
        with (gf1 if idx % 2 == 0 else gf2):
            if st.button(f"🍕 {opt}", key=f"btn_f_{st.session_state.reto_frac_id}_{idx}_{opt}", use_container_width=True):
                if opt == correcta_f:
                    st.balloons()
                    st.success(t["correct"])
                    st.session_state.gemas += 10
                    if st.session_state.gemas % 50 == 0: st.session_state.nivel += 1
                    sincronizar_progreso(st.session_state.estudiante_id, st.session_state.estudiante_nombre, st.session_state.gemas, st.session_state.nivel)
                    nuevo_reto_fracciones()
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.session_state.mostrar_pista_frac = True
                    st.error(t["incorrect"])
                    st.rerun()

# === MUNDO 5: DECIMALES ===
with tab_dec:
    tipo_d = st.session_state.tipo_ejercicio_dec
    d_data = st.session_state.dec_data

    if tipo_d == 1:
        unit_label = "U" if lang == "English" else "U"
        tenths_label = "t" if lang == "English" else "d"
        hundredths_label = "h" if lang == "English" else "c"
        prompt = f"{t['dec_q1']}<br><div class='fraction-visual'><b>{d_data['e']}</b> {unit_label} | <b>{d_data['d']}</b> {tenths_label} | <b>{d_data['c']}</b> {hundredths_label}</div>"
    elif tipo_d == 2:
        prompt = f"{t['dec_q2']}<br><br>💎 <b>A:</b> {d_data['nA']} | 💎 <b>B:</b> {d_data['nB']}"
    else:
        prompt = f"{t['dec_q3']}<br><span style='font-size:32px;' class='highlight-text'><b>{d_data['num_f']} / {d_data['den_f']}</b></span>"

    st.markdown(f'<div class="question-card"><div class="question-badge">{t["tab_dec"]}</div><br>{prompt}</div>', unsafe_allow_html=True)

    if st.session_state.mostrar_pista_dec:
        st.markdown(f'<div class="cpa-box"><b>{t["cpa_title"]}</b><br>• {t["correct_answer_label"]} <b>{st.session_state.dec_correcta}</b></div>', unsafe_allow_html=True)

    gd1, gd2 = st.columns(2)
    for idx, opt in enumerate(st.session_state.dec_opciones):
        display_opt = f"{t['crystal_prefix']} {opt}" if tipo_d == 2 else opt
        with (gd1 if idx % 2 == 0 else gd2):
            if st.button(f"💎 {display_opt}", key=f"btn_d_{st.session_state.reto_dec_id}_{idx}_{opt}", use_container_width=True):
                if opt == st.session_state.dec_correcta:
                    st.balloons()
                    st.success(t["correct"])
                    st.session_state.gemas += 10
                    if st.session_state.gemas % 50 == 0: st.session_state.nivel += 1
                    sincronizar_progreso(st.session_state.estudiante_id, st.session_state.estudiante_nombre, st.session_state.gemas, st.session_state.nivel)
                    time.sleep(0.5)
                    nuevo_reto_decimales()
                    st.rerun()
                else:
                    st.session_state.mostrar_pista_dec = True
                    st.error(t["incorrect"])
                    st.rerun()

# === MUNDO 6: TIENDA ===
with tab_tienda:
    st.caption(t["shop_caption"])
    t_col1, t_col2 = st.columns(2)

    for idx, (item_id, info) in enumerate(TIENDA_ITEMS.items()):
        col_destino = t_col1 if idx % 2 == 0 else t_col2
        con_comprado = item_id in st.session_state.inventario
        con_equipado = st.session_state.equipado[info["tipo"]] == item_id

        with col_destino:
            st.markdown(
                f"""
                <div class="shop-card">
                    <img src="{info['img']}" style="width: 52px; height: 52px; object-fit: contain;" />
                    <div style="font-weight: 800; font-size: 16px; margin-top: 6px;">{info['nombre']}</div>
                    <div style="color: #64748b; font-size: 13px;">{info['tipo']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if not con_comprado:
                if st.button(f"{t['buy']} 🪙 {info['precio']}", key=f"buy_{item_id}", use_container_width=True):
                    if st.session_state.gemas >= info["precio"]:
                        st.session_state.gemas -= info["precio"]
                        st.session_state.inventario.append(item_id)
                        sincronizar_progreso(st.session_state.estudiante_id, st.session_state.estudiante_nombre, st.session_state.gemas, st.session_state.nivel)
                        st.toast(f"¡Comprado: {info['nombre']}!", icon="🎉")
                        st.rerun()
                    else:
                        st.error(t["no_gems"])
            else:
                if con_equipado:
                    if st.button(t["unequip"], key=f"unequip_{item_id}", use_container_width=True):
                        st.session_state.equipado[info["tipo"]] = None
                        st.rerun()
                else:
                    if st.button(t["equip"], key=f"equip_{item_id}", use_container_width=True):
                        st.session_state.equipado[info["tipo"]] = item_id
                        st.toast(f"Equipado: {info['nombre']}")
                        st.rerun()