import base64
from datetime import datetime
import random
import time
import pandas as pd
import streamlit as st

# Intenta importar la conexión de Google Sheets, si no está configurada usará modo local sin fallar
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
# 1. CONFIGURACIÓN Y ESTILOS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Math Quest: Guardianes del Número",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# GENERADORES DE RETOS INFINITOS
# -----------------------------------------------------------------------------
def nuevo_reto_operaciones():
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
    st.session_state.tipo_ejercicio_frac = random.choice([1, 2, 3])
    st.session_state.mostrar_pista_frac = False
    st.session_state.reto_frac_id = time.time()


def nuevo_reto_decimales():
    tipo = random.choice([1, 2, 3])
    st.session_state.tipo_ejercicio_dec = tipo
    st.session_state.mostrar_pista_dec = False
    st.session_state.reto_dec_id = time.time()

    if tipo == 1:
        e = random.randint(0, 5)
        d = random.randint(1, 9)
        c = random.randint(0, 9)
        val_real = round(e + d / 10 + c / 100, 2)

        st.session_state.dec_data = {"e": e, "d": d, "c": c}
        correcta = str(val_real)
        distractoras = [
            str(round(val_real + 0.1, 2)),
            str(round(val_real - 0.01 if val_real > 0.01 else 0.05, 2)),
            f"{e}.{c}{d}",
        ]

        opciones = list(set([correcta] + distractoras))
        random.shuffle(opciones)

        st.session_state.dec_correcta = correcta
        st.session_state.dec_opciones = opciones

    elif tipo == 2:
        base = round(random.uniform(0.1, 9.9), 1)
        diferencia = random.choice([0.01, 0.05, 0.1, 0.15])
        nA = round(base, 2)
        nB = round(base + diferencia, 2)

        if random.choice([True, False]):
            nA, nB = nB, nA

        st.session_state.dec_data = {"nA": nA, "nB": nB}
        st.session_state.dec_correcta = "A" if nA > nB else ("B" if nB > nA else "EQUAL")
        st.session_state.dec_opciones = ["A", "B", "EQUAL"]

    else:
        num_f = random.choice([3, 7, 12, 45, 8, 25, 64, 89])
        den_f = random.choice([10, 100])
        val_real = round(num_f / den_f, 2)

        st.session_state.dec_data = {"num_f": num_f, "den_f": den_f}
        correcta = str(val_real)
        distractoras = [str(round(val_real * 10, 2)), str(round(val_real / 10, 2)), f"0.{num_f}"]

        opciones = list(set([correcta] + distractoras))
        random.shuffle(opciones)

        st.session_state.dec_correcta = correcta
        st.session_state.dec_opciones = opciones


# -----------------------------------------------------------------------------
# INICIALIZACIÓN DE SESSION STATE
# -----------------------------------------------------------------------------
if "tipo_operacion" not in st.session_state:
    nuevo_reto_operaciones()

if "numerador" not in st.session_state:
    nuevo_reto_fracciones()

if "tipo_ejercicio_dec" not in st.session_state:
    nuevo_reto_decimales()

if "gemas" not in st.session_state:
    st.session_state.gemas = 0

if "nivel" not in st.session_state:
    st.session_state.nivel = 1

if "equipado" not in st.session_state:
    st.session_state.equipado = {"Casco": None, "Mascota": None, "Escudo": None}

st.markdown("""
    <style>
    /* -----------------------------------------------------------------------------
       1. FUENTE GLOBAL Y FONDO PRINCIPAL
    ----------------------------------------------------------------------------- */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&family=Nunito:wght@600;800;900&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Fredoka', 'Nunito', sans-serif !important;
        background: #f0f4f9;
        color: #2c3e50;
    }

    /* -----------------------------------------------------------------------------
       2. CONTENEDOR DE LOGO Y SIDEBAR
    ----------------------------------------------------------------------------- */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 3px solid #e2e8f0;
    }

    /* Marco destacado para el Logo del Colegio */
    .logo-container {
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        border: 3px solid #e2e8f0;
        border-radius: 20px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.06);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    
    .logo-container:hover {
        transform: scale(1.03);
    }

    .logo-img {
        max-width: 140px;
        height: auto;
        filter: drop-shadow(0px 4px 8px rgba(0, 0, 0, 0.12));
    }

    /* -----------------------------------------------------------------------------
       3. PESTAÑAS DIVERTIAS (TABS)
    ----------------------------------------------------------------------------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 14px 14px 0 0 !important;
        border: 2px solid #e2e8f0;
        border-bottom: none;
        padding: 10px 20px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        color: #64748b !important;
        transition: all 0.2s ease-in-out;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
        color: #ffffff !important;
        border-color: #4f46e5 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }

    /* -----------------------------------------------------------------------------
       4. TARJETAS DE MUNDOS Y RETOS (GRADIENTES + SOMBRAS 3D)
    ----------------------------------------------------------------------------- */
    .math-card {
        background: linear-gradient(135deg, #4f46e5, #3730a3);
        padding: 24px;
        border-radius: 24px;
        color: white;
        text-align: center;
        font-size: 26px;
        font-weight: 700;
        box-shadow: 0 10px 20px rgba(79, 70, 229, 0.3), inset 0 2px 0 rgba(255,255,255,0.2);
        margin-bottom: 20px;
        border: 3px solid #818cf8;
    }

    .fraction-card {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        padding: 24px;
        border-radius: 24px;
        color: white;
        text-align: center;
        font-size: 24px;
        font-weight: 700;
        box-shadow: 0 10px 20px rgba(245, 158, 11, 0.3), inset 0 2px 0 rgba(255,255,255,0.2);
        margin-bottom: 20px;
        border: 3px solid #fbbf24;
    }

    .decimal-card {
        background: linear-gradient(135deg, #10b981, #047857);
        padding: 24px;
        border-radius: 24px;
        color: white;
        text-align: center;
        font-size: 24px;
        font-weight: 700;
        box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3), inset 0 2px 0 rgba(255,255,255,0.2);
        margin-bottom: 20px;
        border: 3px solid #34d399;
    }

    /* Caja de Pista Pedagógica (CPA) */
    .cpa-box {
        background-color: #ffffff;
        border: 3px dashed #f59e0b;
        border-radius: 20px;
        padding: 22px;
        margin: 20px 0;
        box-shadow: 0 6px 15px rgba(0,0,0,0.04);
        color: #1e293b;
        font-size: 16px;
        line-height: 1.7;
    }

    /* -----------------------------------------------------------------------------
       5. BOTONES ESTILO VIDEOJUEGO (GAMIFIED 3D BUTTONS)
    ----------------------------------------------------------------------------- */
    .stButton > button {
        border-radius: 16px !important;
        font-family: 'Fredoka', sans-serif !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
        border: none !important;
        background: linear-gradient(180deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important;
        box-shadow: 0 6px 0 #1e40af, 0 10px 15px rgba(0,0,0,0.15) !important;
        transition: all 0.1s ease-in-out !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 0 #1e40af, 0 12px 20px rgba(0,0,0,0.2) !important;
        background: linear-gradient(180deg, #60a5fa 0%, #2563eb 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(4px) !important;
        box-shadow: 0 2px 0 #1e40af, 0 4px 6px rgba(0,0,0,0.1) !important;
    }

    /* -----------------------------------------------------------------------------
       6. TARJETAS DE TIENDA Y AVATAR
    ----------------------------------------------------------------------------- */
    .avatar-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 18px;
        text-align: center;
        border: 3px solid #e2e8f0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.04);
        margin-bottom: 15px;
        transition: transform 0.2s ease;
    }

    .avatar-card:hover {
        transform: translateY(-4px);
        border-color: #cbd5e1;
    }

    .fraction-visual {
        font-size: 34px;
        letter-spacing: 6px;
        margin: 15px 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. RENDERIZADOR DE AVATAR MODULAR
# -----------------------------------------------------------------------------
def renderizar_avatar_dinamico(
    img_base: str,
    img_casco: str = None,
    img_escudo: str = None,
    img_mascota: str = None,
    size: int = 90,
):
    capas = f'<img src="{img_base}" style="position:absolute; top:2%; left:2%; width:96%; height:96%; object-fit:contain; z-index:2;" />'

    if img_casco:
        capas += f'<img src="{img_casco}" style="position:absolute; top:-20%; left:15%; width:70%; height:50%; object-fit:contain; z-index:4;" />'

    if img_escudo:
        capas += f'<img src="{img_escudo}" style="position:absolute; bottom:5%; right:-10%; width:40%; height:40%; object-fit:contain; z-index:5;" />'

    if img_mascota:
        capas += f'<img src="{img_mascota}" style="position:absolute; bottom:0%; left:-15%; width:40%; height:40%; object-fit:contain; z-index:3;" />'

    return (
        f'<div style="position:relative; width:{size}px; height:{size}px; display:inline-block; '
        f'vertical-align:middle; background:radial-gradient(circle, #f1f5f9 0%, #e2e8f0 100%); '
        f'border-radius:50%; border:2px solid #cbd5e1; flex-shrink:0; overflow:visible;">{capas}</div>'
    )

# -----------------------------------------------------------------------------
# 3. SELECTOR DE IDIOMA Y DICCIONARIO BILINGÜE
# -----------------------------------------------------------------------------
with st.sidebar:
    if LOGO_COLEGIO_BASE64:
        st.markdown(
            f'''
            <div class="logo-container">
                <img src="{LOGO_COLEGIO_BASE64}" class="logo-img" />
            </div>
            ''',
            unsafe_allow_html=True,
        )
    else:
        st.caption("🏫 *Agrega logo_colegio.png en la carpeta del proyecto*")

    st.title("⚙️ Settings / Configuración")
    lang = st.radio("🌐 Language / Idioma:", options=["Español", "English"], index=0)    

TEXTS = {
    "Español": {
        "title": "🛡️ Math Quest: Guardianes del Número",
        "welcome": "¡Bienvenido, Pequeño Guardián!",
        "input_label": "Ingresa tu Nombre o Código de Estudiante:",
        "select_hero": "Elige tu Héroe Base:",
        "btn_start": "¡Comenzar Aventura! 🚀",
        "level": "Nivel",
        "tab_op": "🌲 Bosque de Operaciones",
        "tab_frac": "🍕 Reino de Partes",
        "tab_dec": "💎 Valle de Decimales",
        "tab_shop": "🛒 Tienda del Guardián",
        "op_mission": "Misión: Resuelve las operaciones para avanzar por el bosque.",
        "op_question": "¿Cuánto es",
        "frac_m1": "Misión: Identifica la fracción representada en la barra.",
        "frac_q1": "¿Qué fracción del cristal está encendida?",
        "frac_m2": "Misión: Análisis conceptual del cristal de poder.",
        "frac_q2": "Si activamos {num} de un total de {den} partes:",
        "frac_q2_sub": "¿Cuál es la fracción activada?",
        "frac_m3": "Misión: Ayuda a los habitantes del reino.",
        "frac_q3": "🍕 Una pizza se cortó en <b>{den} rebanadas iguales</b>.<br>Si Mateo se comió <b>{num} rebanadas</b>,<br>¿qué fracción de la pizza se comió?",
        "dec_mission": "Misión: Descifra la energía decimal del cristal.",
        "dec_m2_prompt": "¿Cuál cristal tiene MÁS energía?<br><br>💎 <b>Cristal A:</b> {nA}<br>💎 <b>Cristal B:</b> {nB}",
        "dec_m3_prompt": "Convierte la siguiente fracción a su forma decimal:<br><br><span style='font-size:36px;'><b>{num_f} / {den_f}</b></span>",
        "cpa_title": "💡 Pista Conceptual (CPA) - Explicación Detallada",
        "correct": "¡Excelente! +10 Gemas 🎉",
        "incorrect": "¡Casi! Revisa la explicación detallada arriba para entender la lógica.",
        "shop_caption": "🛒 **Tienda del Guardián:** Usa tus gemas ganadas para personalizar tu personaje.",
        "buy": "Comprar",
        "equip": "✨ Equipar",
        "unequip": "❌ Desequipar",
        "no_gems": "¡Gemas insuficientes!",
    },
    "English": {
        "title": "🛡️ Math Quest: Number Guardians",
        "welcome": "Welcome, Little Guardian!",
        "input_label": "Enter your Name or Student ID:",
        "select_hero": "Choose your Base Hero:",
        "btn_start": "Start Adventure! 🚀",
        "level": "Level",
        "tab_op": "🌲 Forest of Operations",
        "tab_frac": "🍕 Kingdom of Fractions",
        "tab_dec": "💎 Decimal Valley",
        "tab_shop": "🛒 Guardian Shop",
        "op_mission": "Mission: Solve operations to make your way through the forest.",
        "op_question": "What is",
        "frac_m1": "Mission: Identify the fraction shown on the crystal bar.",
        "frac_q1": "What fraction of the crystal is active?",
        "frac_m2": "Mission: Conceptual analysis of the power crystal.",
        "frac_q2": "If we activate {num} out of a total of {den} parts:",
        "frac_q2_sub": "Which fraction is activated?",
        "frac_m3": "Mission: Help the kingdom inhabitants.",
        "frac_q3": "🍕 A pizza was sliced into <b>{den} equal slices</b>.<br>If Mateo ate <b>{num} slices</b>,<br>what fraction of the pizza did he eat?",
        "dec_mission": "Mission: Decipher the crystal's decimal energy.",
        "dec_m2_prompt": "Which crystal has MORE power?<br><br>💎 <b>Crystal A:</b> {nA}<br>💎 <b>Crystal B:</b> {nB}",
        "dec_m3_prompt": "Convert the following fraction to decimal form:<br><br><span style='font-size:36px;'><b>{num_f} / {den_f}</b></span>",
        "cpa_title": "💡 Conceptual Hint (CPA) - Detailed Explanation",
        "correct": "Great Job! +10 Gems 🎉",
        "incorrect": "Almost! Read the detailed explanation above to master the logic.",
        "shop_caption": "🛒 **Guardian Shop:** Use your earned gems to customize your avatar.",
        "buy": "Buy",
        "equip": "✨ Equip",
        "unequip": "❌ Unequip",
        "no_gems": "Not enough gems!",
    },
}

t = TEXTS[lang]

# -----------------------------------------------------------------------------
# 4. CONSTANTES GLOBALES
# -----------------------------------------------------------------------------
CDN_BASE = "https://openmoji.org/data/color/svg"

PERSONAJES_BASE = {
    "guardian_escolar": {"nombre": "Isabelino", "img": AVATAR_ESCOLAR_BASE64},
    "mago": {"nombre": "Number Wizard / Mago", "img": f"{CDN_BASE}/1F9D9.svg"},
    "guardiana": {"nombre": "Forest Guardian / Guardiana", "img": f"{CDN_BASE}/1F9DC.svg"},
    "bot": {"nombre": "Cyber-Bot 3000", "img": f"{CDN_BASE}/1F916.svg"},
    "guerrero": {"nombre": "Valor Knight / Guerrero", "img": f"{CDN_BASE}/1F977.svg"},
}

TIENDA_ITEMS = {
    "sombrero_mago": {
        "nombre": "Magic Hat" if lang == "English" else "Sombrero Mágico",
        "img": f"{CDN_BASE}/1F3A9.svg",
        "precio": 30,
        "tipo": "Casco",
    },
    "corona_real": {
        "nombre": "Wisdom Crown" if lang == "English" else "Corona de Sabiduría",
        "img": f"{CDN_BASE}/1F451.svg",
        "precio": 60,
        "tipo": "Casco",
    },
    "dragonsito": {
        "nombre": "Fire Dragon" if lang == "English" else "Dragón de Fuego",
        "img": f"{CDN_BASE}/1F409.svg",
        "precio": 80,
        "tipo": "Mascota",
    },
    "gato_sabio": {
        "nombre": "Astro Cat" if lang == "English" else "Gato Astro",
        "img": f"{CDN_BASE}/1F431.svg",
        "precio": 40,
        "tipo": "Mascota",
    },
    "escudo_estelar": {
        "nombre": "Cosmic Shield" if lang == "English" else "Escudo Cósmico",
        "img": f"{CDN_BASE}/1F6E1.svg",
        "precio": 50,
        "tipo": "Escudo",
    },
}

# -----------------------------------------------------------------------------
# 5. FUNCIONES DE CONEXIÓN
# -----------------------------------------------------------------------------
def sincronizar_progreso(estudiante_id, nombre, gemas, nivel):
    if not HAS_GSHEETS:
        return
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_estudiantes = conn.read(worksheet="Estudiantes", ttl=0)
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if estudiante_id in df_estudiantes["ID_Estudiante"].astype(str).values:
            df_estudiantes.loc[
                df_estudiantes["ID_Estudiante"].astype(str) == estudiante_id,
                ["Gemas", "Nivel", "Ultimo_Acceso"],
            ] = [gemas, nivel, ahora]
        else:
            nuevo_registro = pd.DataFrame(
                [
                    {
                        "ID_Estudiante": estudiante_id,
                        "Nombre": nombre,
                        "Gemas": gemas,
                        "Nivel": nivel,
                        "Ultimo_Acceso": ahora,
                    }
                ]
            )
            df_estudiantes = pd.concat([df_estudiantes, nuevo_registro], ignore_index=True)

        conn.update(worksheet="Estudiantes", data=df_estudiantes)
    except Exception:
        pass

# -----------------------------------------------------------------------------
# 6. PANTALLA DE LOGIN
# -----------------------------------------------------------------------------
if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = False

if not st.session_state.usuario_activo:
    st.title(t["title"])
    st.subheader(t["welcome"])

    with st.form("form_login"):
        nombre_input = st.text_input(t["input_label"])

        personaje_sel = st.selectbox(
            t["select_hero"],
            options=list(PERSONAJES_BASE.keys()),
            format_func=lambda x: f"{PERSONAJES_BASE[x]['nombre']}",
        )

        btn_ingresar = st.form_submit_button(t["btn_start"], use_container_width=True)

        if btn_ingresar and nombre_input.strip():
            est_id = nombre_input.strip().lower().replace(" ", "_")
            st.session_state.estudiante_id = est_id
            st.session_state.estudiante_nombre = nombre_input.strip()
            st.session_state.personaje_base = personaje_sel
            st.session_state.gemas = 100
            st.session_state.nivel = 1
            st.session_state.inventario = []
            st.session_state.equipado = {"Casco": None, "Mascota": None, "Escudo": None}
            st.session_state.usuario_activo = True
            st.rerun()
    st.stop()

# -----------------------------------------------------------------------------
# 7. HUD SUPERIOR CON AVATAR
# -----------------------------------------------------------------------------
hero_base_key = st.session_state.get("personaje_base", "mago")
img_base = PERSONAJES_BASE[hero_base_key]["img"]

casco_id = st.session_state.equipado.get("Casco")
mascota_id = st.session_state.equipado.get("Mascota")
escudo_id = st.session_state.equipado.get("Escudo")

img_casco = TIENDA_ITEMS[casco_id]["img"] if casco_id else None
img_mascota = TIENDA_ITEMS[mascota_id]["img"] if mascota_id else None
img_escudo = TIENDA_ITEMS[escudo_id]["img"] if escudo_id else None

avatar_html = renderizar_avatar_dinamico(
    img_base=img_base,
    img_casco=img_casco,
    img_escudo=img_escudo,
    img_mascota=img_mascota,
    size=75,
)

nombre_usuario = st.session_state.get("estudiante_nombre", "Jugador")

col_hud1, col_hud2, col_hud3 = st.columns([2.5, 1, 1])

with col_hud1:
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:12px;">'
        f"{avatar_html}"
        f'<span style="font-size:20px; font-weight:bold; color:#2c3e50;">{nombre_usuario}</span>'
        f"</div>",
        unsafe_allow_html=True,
    )

with col_hud2:
    st.markdown(f"### 🪙 `{st.session_state.gemas}`")

with col_hud3:
    st.markdown(f"### 🌟 {t['level']} `{st.session_state.nivel}`")

st.divider()

# -----------------------------------------------------------------------------
# 8. PESTAÑAS PRINCIPALES
# -----------------------------------------------------------------------------
tab_op, tab_frac, tab_dec, tab_tienda = st.tabs(
    [t["tab_op"], t["tab_frac"], t["tab_dec"], t["tab_shop"]]
)

# =============================================================================
# MUNDO 1: OPERACIONES
# =============================================================================
with tab_op:
    tipo_op = st.session_state.tipo_operacion
    n1, n2 = st.session_state.num1, st.session_state.num2
    correcta_o = st.session_state.correcta_op

    st.caption(t["op_mission"])
    st.markdown(
        f'<div class="math-card">{t["op_question"]} {n1} {"×" if tipo_op == "mult" else "÷"} {n2}?</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.mostrar_pista_op:
        if tipo_op == "mult":
            suma_str = " + ".join([str(n2)] * n1)
            if lang == "English":
                explicacion_op = f"""
                    <b>🔍 Conceptual Breakdown:</b><br>
                    • <b>What is Multiplication?</b> Multiplication is a fast way of doing repeated additions of the same size.<br>
                    • <b>The Meaning of {n1} × {n2}:</b> Imagine organizing items into a grid. You have <b>{n1} rows (groups)</b> and each row contains <b>{n2} elements</b>.<br>
                    • <b>Step-by-Step Addition:</b> Instead of counting one by one, you add the same group: <code>{suma_str}</code>.<br>
                    • <b>Conclusion:</b> Accumulating those {n1} equal groups gives a total of <b style="color:#d35400;">{correcta_o}</b>.
                """
            else:
                explicacion_op = f"""
                    <b>🔍 Desglose Conceptual:</b><br>
                    • <b>¿Qué es Multiplicar?</b> La multiplicación es un atajo para sumar varias veces una misma cantidad sin cansarse.<br>
                    • <b>Significado de {n1} × {n2}:</b> Imagina organizar manzanas en filas. Tienes <b>{n1} filas (grupos)</b> y en cada fila colocas <b>{n2} elementos</b>.<br>
                    • <b>Suma Repetida:</b> En lugar de contar de 1 en 1, sumas cada grupo completo: <code>{suma_str}</code>.<br>
                    • <b>Conclusión:</b> Al acumular esos {n1} grupos iguales obtienes un total de <b style="color:#d35400;">{correcta_o}</b>.
                """

            st.markdown(
                f"""
                <div class="cpa-box">
                    <div style="color: #d35400; font-weight: bold; font-size: 18px;">{t["cpa_title"]}</div>
                    <p style="margin-top:8px;">{explicacion_op}</p>
                </div>
            """,
                unsafe_allow_html=True,
            )
            for i in range(n1):
                st.write(f"**Group / Grupo {i+1}:** " + "🍏 " * n2)
        else:
            if lang == "English":
                explicacion_op = f"""
                    <b>🔍 Conceptual Breakdown:</b><br>
                    • <b>What is Division?</b> Division is the opposite of multiplication: it means fair sharing or splitting a big total into equal parts.<br>
                    • <b>The Meaning of {n1} ÷ {n2}:</b> You start with a total of <b>{n1} items</b> and want to distribute them evenly into <b>{n2} equal boxes</b>.<br>
                    • <b>Fair Distribution:</b> You place 1 item in each box repeatedly until the total of {n1} is completely exhausted.<br>
                    • <b>Conclusion:</b> Each box ends up with exactly <b style="color:#d35400;">{correcta_o} elements</b> because {correcta_o} × {n2} = {n1}.
                """
            else:
                explicacion_op = f"""
                    <b>🔍 Desglose Conceptual:</b><br>
                    • <b>¿Qué es Dividir?</b> La división es la operación inversa a la multiplicación: consiste en hacer un reparto equitativo o "justo".<br>
                    • <b>Significado de {n1} ÷ {n2}:</b> Empiezas con un gran total de <b>{n1} elementos</b> y debes repartirlos en partes iguales entre <b>{n2} cajas</b>.<br>
                    • <b>Reparto Paso a Paso:</b> Vas entregando elementos uno a uno a cada caja hasta que el total de {n1} se agota por completo.<br>
                    • <b>Conclusión:</b> A cada caja le corresponden exactamente <b style="color:#d35400;">{correcta_o} elementos</b> porque {correcta_o} × {n2} = {n1}.
                """

            st.markdown(
                f"""
                <div class="cpa-box">
                    <div style="color: #d35400; font-weight: bold; font-size: 18px;">{t["cpa_title"]}</div>
                    <p style="margin-top:8px;">{explicacion_op}</p>
                </div>
            """,
                unsafe_allow_html=True,
            )
            for i in range(n2):
                st.write(f"**Box / Caja {i+1}:** " + "🍎 " * correcta_o)
        st.divider()

    opciones_o = list({correcta_o, correcta_o + 2, max(1, correcta_o - 1), correcta_o + 3})
    random.seed(int(st.session_state.reto_op_id * 1000))
    random.shuffle(opciones_o)

    g1, g2 = st.columns(2)
    for idx, opt in enumerate(opciones_o):
        col_dest = g1 if idx % 2 == 0 else g2
        with col_dest:
            if st.button(f"👉 {opt}", key=f"btn_o_{st.session_state.reto_op_id}_{idx}_{opt}", use_container_width=True):
                if opt == correcta_o:
                    st.balloons()
                    st.success(t["correct"])
                    st.session_state.gemas += 10
                    if st.session_state.gemas % 50 == 0:
                        st.session_state.nivel += 1

                    sincronizar_progreso(
                        st.session_state.estudiante_id,
                        st.session_state.estudiante_nombre,
                        st.session_state.gemas,
                        st.session_state.nivel,
                    )
                    time.sleep(0.5)
                    nuevo_reto_operaciones()
                    st.rerun()
                else:
                    st.session_state.mostrar_pista_op = True
                    st.error(t["incorrect"])
                    st.rerun()

# =============================================================================
# MUNDO 2: FRACCIONES
# =============================================================================
with tab_frac:
    num, den = st.session_state.numerador, st.session_state.denominador
    tipo = st.session_state.tipo_ejercicio_frac
    reto_id = st.session_state.get("reto_frac_id", time.time())

    if tipo == 1:
        st.caption(t["frac_m1"])
        bloques = "🟩 " * num + "⬜ " * (den - num)
        st.markdown(
            f'<div class="fraction-card">{t["frac_q1"]}<div class="fraction-visual">{bloques}</div></div>',
            unsafe_allow_html=True,
        )
        correcta_f = f"{num}/{den}"
        distractoras = [
            f"{den - num}/{den}",
            f"{num}/{den + 1 if den < 8 else den - 1}",
            f"{num + 1 if num < den - 1 else 1}/{den}",
        ]
    elif tipo == 2:
        st.caption(t["frac_m2"])
        bloques = "🟦 " * num + "⬜ " * (den - num)
        q2_txt = t["frac_q2"].format(num=num, den=den)
        st.markdown(
            f'<div class="fraction-card">{q2_txt}<div class="fraction-visual">{bloques}</div>{t["frac_q2_sub"]}</div>',
            unsafe_allow_html=True,
        )
        correcta_f = f"{num}/{den}"
        distractoras = [
            f"{num}/{den - 1 if den > 2 else den + 2}",
            f"{den}/{num}",
            f"{num + 1}/{den}",
        ]
    else:
        st.caption(t["frac_m3"])
        q3_txt = t["frac_q3"].format(num=num, den=den)
        st.markdown(f'<div class="fraction-card">{q3_txt}</div>', unsafe_allow_html=True)
        correcta_f = f"{num}/{den}"
        distractoras = [f"{den - num}/{den}", f"{num}/{den + 2}", f"{den}/{num}"]

    if st.session_state.mostrar_pista_frac:
        if lang == "English":
            exp_frac = f"""
                <b>🔍 Anatomy of the Fraction <span style="color:#d35400;">{num}/{den}</span>:</b><br>
                • <b>Denominator (Bottom Number = {den}):</b> This represents the <i>Unit Division</i>. It tells us that 1 whole object was divided into exactly <b>{den} identical equal-sized pieces</b>.<br>
                • <b>Numerator (Top Number = {num}):</b> This represents the <i>Selection or Count</i>. It tells us how many of those equal pieces we are active, taking, or highlighting (<b>{num} pieces</b>).<br>
                • <b>Why not swap them?</b> If you wrote <code>{den}/{num}</code>, you would be saying you took {den} parts from a total of {num}, which changes the entire physical meaning!<br>
                <i>💡 Golden Rule: Bottom = Total cuts made | Top = Cuts taken!</i>
            """
        else:
            exp_frac = f"""
                <b>🔍 Anatomía de la Fracción <span style="color:#d35400;">{num}/{den}</span>:</b><br>
                • <b>Denominador (Número de abajo = {den}):</b> Representa la <i>Unidad de Medida</i>. Nos dice que el objeto entero fue dividido en exactamente <b>{den} partes completamente iguales</b>.<br>
                • <b>Numerador (Número de arriba = {num}):</b> Representa el <i>Conteo o Elección</i>. Indica cuántas de esas partes exactas estamos tomando, pintando o activando (<b>{num} partes</b>).<br>
                • <b>¿Por qué no al revés?</b> Si escribieras <code>{den}/{num}</code>, estarías diciendo que tienes más pedazos tomados que los cortes totales que existían en la unidad.<br>
                <i>💡 Regla de Oro: ¡Abajo van los cortes totales; arriba los pedazos seleccionados!</i>
            """
        st.markdown(
            f'<div class="cpa-box"><div style="color: #e67e22; font-weight: bold; font-size:18px;">{t["cpa_title"]}</div><p style="margin-top:8px;">{exp_frac}</p></div>',
            unsafe_allow_html=True,
        )

    opciones_f = list(set([correcta_f] + distractoras))
    random.shuffle(opciones_f)

    gf1, gf2 = st.columns(2)
    for idx, opt in enumerate(opciones_f):
        col_dest = gf1 if idx % 2 == 0 else gf2
        with col_dest:
            btn_key = f"btn_f_{reto_id}_{idx}_{opt}"

            if st.button(f"🍕 {opt}", key=btn_key, use_container_width=True):
                if opt == correcta_f:
                    st.balloons()
                    st.success(t["correct"])
                    st.session_state.gemas += 10
                    if st.session_state.gemas % 50 == 0:
                        st.session_state.nivel += 1

                    sincronizar_progreso(
                        st.session_state.estudiante_id,
                        st.session_state.estudiante_nombre,
                        st.session_state.gemas,
                        st.session_state.nivel,
                    )

                    nuevo_reto_fracciones()
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.session_state.mostrar_pista_frac = True
                    st.error(t["incorrect"])
                    st.rerun()

# =============================================================================
# MUNDO 3: DECIMALES
# =============================================================================
with tab_dec:
    st.caption(t["dec_mission"])

    tipo_d = st.session_state.tipo_ejercicio_dec
    d_data = st.session_state.dec_data

    if tipo_d == 1:
        e, d_val, c = d_data["e"], d_data["d"], d_data["c"]
        u_lbl = "Ones / Unidades" if lang == "English" else "Unidades"
        d_lbl = "Tenths / Décimas" if lang == "English" else "Décimas"
        c_lbl = "Hundredths / Centésimas" if lang == "English" else "Centésimas"
        q_lbl = (
            "What decimal number do these blocks represent?"
            if lang == "English"
            else "¿Qué número decimal representan estos bloques?"
        )

        prompt_html = f"{q_lbl}<br><div class='fraction-visual'><b>{e}</b> {u_lbl} 🟩 | <b>{d_val}</b> {d_lbl} 🟨 | <b>{c}</b> {c_lbl} 🟦</div>"
    elif tipo_d == 2:
        prompt_html = t["dec_m2_prompt"].format(nA=d_data["nA"], nB=d_data["nB"])
    else:
        prompt_html = t["dec_m3_prompt"].format(num_f=d_data["num_f"], den_f=d_data["den_f"])

    st.markdown(f'<div class="decimal-card">{prompt_html}</div>', unsafe_allow_html=True)

    if st.session_state.mostrar_pista_dec:
        if tipo_d == 1:
            e, d_val, c = d_data["e"], d_data["d"], d_data["c"]
            val_calc = round(e + d_val / 10 + c / 100, 2)
            if lang == "English":
                exp_dec = f"""
                    <b>🔍 Understanding Place Value & Decimal Scale:</b><br>
                    • <b>The Decimal Dot (.):</b> Acts as a boundary. Everything to the left is a <i>Whole Unit</i>; everything to the right is a <i>Fractional Part</i>.<br>
                    • <b>Ones (Left of dot = {e}):</b> Represents whole blocks. Value: <b>{e}</b>.<br>
                    • <b>Tenths (1st digit right of dot = {d_val}):</b> Each tenth is 1 whole block sliced into 10 strips (1/10 = 0.1). Value: {d_val} × 0.1 = <b>{d_val/10}</b>.<br>
                    • <b>Hundredths (2nd digit right of dot = {c}):</b> Each hundredth is 1 whole block sliced into 100 tiny cubes (1/100 = 0.01). Value: {c} × 0.01 = <b>{c/100}</b>.<br>
                    • <b>Combined Total Value:</b> {e} + {d_val/10} + {c/100} = <b style="color:#27ae60; font-size:18px;">{val_calc}</b>.
                """
            else:
                exp_dec = f"""
                    <b>🔍 Comprendiendo el Valor Posicional y la Escala Decimal:</b><br>
                    • <b>El Punto/Coma Decimal (.):</b> Funciona como una frontera. A la izquierda están los <i>Enteros</i>; a la derecha están los <i>Pedazos de Entero</i>.<br>
                    • <b>Unidades (A la izquierda = {e}):</b> Bloques completos sin cortar. Valor: <b>{e}</b>.<br>
                    • <b>Décimas (1ª posición a la derecha = {d_val}):</b> Cortamos 1 entero en 10 tiras (1/10 = 0.1). Valor: {d_val} × 0.1 = <b>{d_val/10}</b>.<br>
                    • <b>Centésimas (2ª posición a la derecha = {c}):</b> Cortamos 1 entero en 10 cubitos (1/100 = 0.01). Valor: {c} × 0.01 = <b>{c/100}</b>.<br>
                    • <b>Valor Total Sumado:</b> {e} + {d_val/10} + {c/100} = <b style="color:#27ae60; font-size:18px;">{val_calc}</b>.
                """
        elif tipo_d == 2:
            nA, nB = d_data["nA"], d_data["nB"]
            if lang == "English":
                exp_dec = f"""
                    <b>🔍 Step-by-Step Decimal Comparison ({nA} vs {nB}):</b><br>
                    • <b>Rule 1 (Whole Numbers):</b> Check the numbers before the decimal point first. Whichever has a larger whole number is bigger.<br>
                    • <b>Rule 2 (Tenths Position):</b> If wholes are equal, inspect the 1st position after the dot (Tenths). Larger tenths = Larger number.<br>
                    • <b>Rule 3 (Hundredths Position):</b> If tenths are also equal, move to the 2nd position (Hundredths).<br>
                    • <b>Analysis:</b> Comparing position by position reveals that <b style="color:#27ae60;">{max(nA, nB)}</b> holds higher positional weight than {min(nA, nB)}.
                """
            else:
                exp_dec = f"""
                    <b>🔍 Comparación Paso a Paso de Decimales ({nA} vs {nB}):</b><br>
                    • <b>Regla 1 (Parte Entera):</b> Compara primero los números antes del punto. El que tenga mayor entero es el más grande.<br>
                    • <b>Regla 2 (Posición de Décimas):</b> Si los enteros son iguales, mira la 1ª cifra tras el punto (Décimas). Mayor décima = Número mayor.<br>
                    • <b>Regla 3 (Posición de Centésimas):</b> Si las décimas coinciden, desempata con la 2ª cifra tras el punto (Centésimas).<br>
                    • <b>Análisis:</b> Al evaluar posición por posición, notamos que <b style="color:#27ae60;">{max(nA, nB)}</b> tiene un peso posicional superior a {min(nA, nB)}.
                """
        else:
            num_f, den_f = d_data["num_f"], d_data["den_f"]
            res = round(num_f / den_f, 2)
            if lang == "English":
                exp_dec = f"""
                    <b>🔍 How Base-10 Fractions Become Decimals ({num_f}/{den_f}):</b><br>
                    • <b>Base-10 Connection:</b> Decimals are just special shorthand for fractions with denominators of 10, 100, 1000, etc.<br>
                    • <b>Dividing by 10:</b> Shifts the decimal point <b>1 place to the left</b> (creates Tenths).<br>
                    • <b>Dividing by 100:</b> Shifts the decimal point <b>2 places to the left</b> (creates Hundredths).<br>
                    • <b>Calculation:</b> Taking {num_f} and dividing by {den_f} moves the scale to give exactly <b style="color:#27ae60;">{res}</b>.
                """
            else:
                exp_dec = f"""
                    <b>🔍 Cómo las Fracciones Base-10 se Convierten en Decimales ({num_f}/{den_f}):</b><br>
                    • <b>Conexión Directa:</b> Un número decimal es solo una forma corta de escribir una fracción que está dividida entre 10, 100, 1000, etc.<br>
                    • <b>Dividir entre 10:</b> Desplaza el punto decimal <b>1 espacio hacia la izquierda</b> (crea Décimas).<br>
                    • <b>Dividir entre 100:</b> Desplaza el punto decimal <b>2 espacios hacia la izquierda</b> (crea Centésimas).<br>
                    • <b>Cálculo:</b> Tomar el número {num_f} y dividirlo entre {den_f} mueve la escala posicional resultando en <b style="color:#27ae60;">{res}</b>.
                """

        st.markdown(
            f"""
            <div class="cpa-box">
                <div style="color: #27ae60; font-weight: bold; font-size:18px;">{t["cpa_title"]}</div>
                <p style="margin-top:8px;">{exp_dec}</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

    correcta_d = st.session_state.dec_correcta
    opciones_d = st.session_state.dec_opciones

    gd1, gd2 = st.columns(2)
    for idx, opt in enumerate(opciones_d):
        col_dest = gd1 if idx % 2 == 0 else gd2

        if tipo_d == 2:
            if opt == "A":
                display_opt = (
                    f"Crystal A ({d_data['nA']}) > Crystal B"
                    if lang == "English"
                    else f"Cristal A ({d_data['nA']}) es MAYOR"
                )
            elif opt == "B":
                display_opt = (
                    f"Crystal B ({d_data['nB']}) > Crystal A"
                    if lang == "English"
                    else f"Cristal B ({d_data['nB']}) es MAYOR"
                )
            else:
                display_opt = "Both are EQUAL" if lang == "English" else "Ambos son IGUALES"
        else:
            display_opt = opt

        with col_dest:
            if st.button(
                f"💎 {display_opt}",
                key=f"btn_d_{st.session_state.reto_dec_id}_{idx}_{opt}",
                use_container_width=True,
            ):
                if opt == correcta_d:
                    st.balloons()
                    st.success(t["correct"])
                    st.session_state.gemas += 10
                    if st.session_state.gemas % 50 == 0:
                        st.session_state.nivel += 1

                    sincronizar_progreso(
                        st.session_state.estudiante_id,
                        st.session_state.estudiante_nombre,
                        st.session_state.gemas,
                        st.session_state.nivel,
                    )
                    time.sleep(0.5)
                    nuevo_reto_decimales()
                    st.rerun()
                else:
                    st.session_state.mostrar_pista_dec = True
                    st.error(t["incorrect"])
                    st.rerun()

# =============================================================================
# MUNDO 4: TIENDA DE ÍTEMS
# =============================================================================
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
                <div class="avatar-card">
                    <img src="{info['img']}" style="width: 50px; height: 50px; object-fit: contain;" />
                    <div style="font-weight: bold; margin-top: 5px;">{info['nombre']}</div>
                    <div style="color: #888; font-size: 14px;">{info['tipo']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if not con_comprado:
                if st.button(
                    f"{t['buy']} 🪙 {info['precio']}",
                    key=f"buy_{item_id}",
                    use_container_width=True,
                ):
                    if st.session_state.gemas >= info["precio"]:
                        st.session_state.gemas -= info["precio"]
                        st.session_state.inventario.append(item_id)
                        sincronizar_progreso(
                            st.session_state.estudiante_id,
                            st.session_state.estudiante_nombre,
                            st.session_state.gemas,
                            st.session_state.nivel,
                        )
                        st.toast(f"Bought / Compraste {info['nombre']}!", icon="🎉")
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
                        st.toast(f"Equipped / Equipaste {info['nombre']}")
                        st.rerun()