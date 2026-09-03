import base64
from datetime import datetime
import random
import time
import pandas as pd
import streamlit as st

import cpa

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
# 2. CSS — UI/UX para 8-11 anios (ver DESIGN_NOTES.md)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
/* =============================================================================
   MATH QUEST — GUARDIANES DEL NÚMERO
   Hoja de estilos para Streamlit · Edad objetivo: 8–11 años (3º–6º primaria)
   -----------------------------------------------------------------------------
   Principios aplicados (ver DESIGN_NOTES.md para fuentes):
   1. Objetivos táctiles grandes  -> min 48px alto, 56px en botones de respuesta
   2. Tipografía legible          -> 18px base, 1.6 line-height, 0.01em tracking
   3. Feedback inmediato y visible-> animaciones de acierto/error, color + icono
   4. Carga cognitiva baja        -> una acción principal por pantalla, jerarquía
   5. Color nunca solo            -> siempre color + forma + icono (daltonismo)
   6. Contraste AA/AAA            -> texto principal >= 7:1 sobre su fondo
   7. Afordancia física ("3D")    -> los botones parecen presionables
   8. Movimiento respetuoso       -> prefers-reduced-motion desactiva todo
   ============================================================================= */

@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@600;700;800;900&display=swap');

/* -----------------------------------------------------------------------------
   0. TOKENS DE DISEÑO
   Cambiar aquí = cambiar todo el tema. No hay colores "sueltos" más abajo.
   -------------------------------------------------------------------------- */
:root {
    /* --- Marca / acentos --- */
    --mq-primary:        #4f46e5;   /* Índigo: acción principal */
    --mq-primary-dark:   #3730a3;   /* Borde inferior 3D */
    --mq-primary-light:  #eef2ff;   /* Fondos suaves */
    --mq-primary-hover:  #4338ca;

    --mq-success:        #16a34a;   /* Acierto */
    --mq-success-dark:   #15803d;
    --mq-success-light:  #f0fdf4;
    --mq-success-border: #86efac;

    --mq-warning:        #f59e0b;   /* Pista / atención */
    --mq-warning-light:  #fffbeb;
    --mq-warning-border: #fcd34d;

    --mq-danger:         #e11d48;   /* Error — rosa, NO rojo alarma */
    --mq-danger-light:   #fff1f2;
    --mq-danger-border:  #fda4af;

    --mq-gem:            #0891b2;   /* Gemas / economía del juego */
    --mq-xp:             #f59e0b;   /* Nivel / estrellas */

    /* --- Neutros --- */
    --mq-bg:             #f2f7ff;   /* Fondo de app: azul cielo muy suave  */
    --mq-surface:        #ffffff;
    --mq-surface-alt:    #f8fafc;
    --mq-border:         #dbe4f0;
    --mq-border-strong:  #b9c7db;
    --mq-text:           #172033;   /* 14.8:1 sobre blanco */
    --mq-text-soft:      #4a5768;   /* 7.4:1  sobre blanco (AAA texto grande) */

    /* --- Tipografía --- */
    --mq-font: 'Fredoka', 'Nunito', 'Segoe UI', system-ui, sans-serif;
    --mq-fs-base:   18px;   /* mínimo recomendado para lectores jóvenes */
    --mq-fs-lg:     22px;
    --mq-fs-xl:     28px;
    --mq-fs-answer: 26px;   /* números dentro de los botones de respuesta */
    --mq-lh:        1.65;

    /* --- Forma y profundidad --- */
    --mq-radius-sm:  14px;
    --mq-radius:     22px;
    --mq-radius-lg:  30px;
    --mq-lift:       6px;    /* grosor del "borde inferior" 3D */
    --mq-shadow:     0 10px 24px -10px rgba(23, 32, 51, 0.18);
    --mq-shadow-lg:  0 18px 38px -14px rgba(79, 70, 229, 0.28);

    /* --- Ritmo --- */
    --mq-gap: 18px;
    --mq-tap: 56px;          /* altura mínima de zona táctil */
    --mq-ease: cubic-bezier(.34, 1.56, .64, 1);  /* rebote suave, "jugoso" */
}

/* -----------------------------------------------------------------------------
   1. BASE
   -------------------------------------------------------------------------- */
html, body, .stApp, [class*="css"] {
    font-family: var(--mq-font) !important;
    color: var(--mq-text) !important;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
}

.stApp {
    /* Fondo con "textura" muy sutil: da calidez sin distraer del contenido */
    background-color: var(--mq-bg) !important;
    background-image:
        radial-gradient(circle at 12% 8%,  rgba(129,140,248,.13) 0, transparent 42%),
        radial-gradient(circle at 88% 4%,  rgba(45,212,191,.12)  0, transparent 38%),
        radial-gradient(circle at 50% 100%, rgba(251,191,36,.10) 0, transparent 45%);
    background-attachment: fixed;
}

.stApp p,
.stApp li,
.stApp label,
.stApp .stMarkdown {
    font-size: var(--mq-fs-base) !important;
    line-height: var(--mq-lh) !important;
    letter-spacing: .01em;
}

/* Bloque principal: ancho cómodo de lectura (≈60 caracteres por línea) */
.block-container {
    padding-top: 2.2rem !important;
    padding-bottom: 5rem !important;
    max-width: 900px;
}

h1, h2, h3, h4 {
    font-family: var(--mq-font) !important;
    font-weight: 700 !important;
    color: var(--mq-text) !important;
    letter-spacing: -.01em;
}
h1 { font-size: 40px !important; line-height: 1.2 !important; }
h2 { font-size: 30px !important; }
h3 { font-size: 24px !important; }

/* Streamlit oculto: menú y footer no aportan nada a un niño de 9 años */
#MainMenu, footer, .stDeployButton { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }

/* Foco visible SIEMPRE — navegación por teclado y por tablet con teclado */
*:focus-visible {
    outline: 4px solid var(--mq-warning) !important;
    outline-offset: 3px !important;
    border-radius: var(--mq-radius-sm);
}

/* -----------------------------------------------------------------------------
   2. BARRA LATERAL
   -------------------------------------------------------------------------- */
[data-testid="stSidebar"] {
    background: var(--mq-surface) !important;
    border-right: 4px solid var(--mq-border) !important;
    box-shadow: 6px 0 24px -12px rgba(23,32,51,.14);
}
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] p {
    font-size: 17px !important;
    font-weight: 600 !important;
}

/* El logo del colegio: ancla de confianza, visible pero no protagonista */
.logo-container {
    background: linear-gradient(150deg, #ffffff 0%, var(--mq-primary-light) 100%);
    border: 3px solid var(--mq-border);
    border-radius: var(--mq-radius);
    padding: 18px;
    text-align: center;
    box-shadow: var(--mq-shadow);
    margin-bottom: 26px;
}
.logo-img { max-width: 140px; height: auto; }

/* Selector de idioma como par de "pastillas" grandes y tocables */
[data-testid="stSidebar"] [role="radiogroup"] { gap: 10px !important; }
[data-testid="stSidebar"] [role="radiogroup"] label {
    background: var(--mq-surface-alt);
    border: 2px solid var(--mq-border);
    border-radius: var(--mq-radius-sm);
    padding: 12px 14px !important;
    min-height: 48px;
    display: flex;
    align-items: center;
    cursor: pointer;
    transition: all .16s var(--mq-ease);
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    border-color: var(--mq-primary);
    background: var(--mq-primary-light);
    transform: translateX(3px);
}

/* -----------------------------------------------------------------------------
   3. HUD — identidad, gemas y nivel
   El niño debe poder responder "¿quién soy y cómo voy?" en menos de 1 segundo.
   -------------------------------------------------------------------------- */
.hud-card {
    background: var(--mq-surface);
    border: 3px solid var(--mq-border);
    border-bottom: var(--mq-lift) solid var(--mq-border-strong);
    border-radius: var(--mq-radius);
    padding: 14px 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--mq-gap);
    margin-bottom: 22px;
    box-shadow: var(--mq-shadow);
}

/* Contadores (💎 gemas / ⭐ nivel) escritos con `code` por Streamlit */
.stApp code {
    font-family: var(--mq-font) !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    background: var(--mq-primary-light) !important;
    color: var(--mq-primary) !important;
    padding: 4px 14px !important;
    border-radius: var(--mq-radius-sm) !important;
    border: 2px solid #c7d2fe !important;
}

/* Micro-latido al cambiar el marcador: refuerza la recompensa */
@keyframes mq-pop {
    0%   { transform: scale(1); }
    45%  { transform: scale(1.22); }
    100% { transform: scale(1); }
}
.stApp h3 code { animation: mq-pop .5s var(--mq-ease); }

/* -----------------------------------------------------------------------------
   4. PESTAÑAS = "MUNDOS" DEL JUEGO
   Deben leerse como fichas de un tablero, no como pestañas de navegador.
   -------------------------------------------------------------------------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background: transparent;
    padding: 4px 0 12px;
    flex-wrap: wrap;                /* en móvil bajan de línea, no se comprimen */
    border-bottom: none !important;
}

.stTabs [data-baseweb="tab"] {
    background: var(--mq-surface) !important;
    border: 3px solid var(--mq-border) !important;
    border-bottom: 5px solid var(--mq-border-strong) !important;
    border-radius: var(--mq-radius-sm) !important;
    padding: 12px 20px !important;
    min-height: 52px;
    font-size: 17px !important;
    font-weight: 600 !important;
    color: var(--mq-text-soft) !important;
    transition: transform .14s var(--mq-ease), background .14s, border-color .14s;
}
.stTabs [data-baseweb="tab"]:hover {
    transform: translateY(-3px);
    border-color: var(--mq-primary) !important;
    background: var(--mq-primary-light) !important;
    color: var(--mq-primary) !important;
}

/* Estado activo: color + elevación + peso. Tres señales, no solo color. */
.stTabs [aria-selected="true"] {
    background: var(--mq-primary) !important;
    border-color: var(--mq-primary-hover) !important;
    border-bottom: 5px solid var(--mq-primary-dark) !important;
    color: #ffffff !important;
    transform: translateY(-3px);
    box-shadow: var(--mq-shadow-lg);
}
.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span { color: #fff !important; font-weight: 700 !important; }

/* Streamlit dibuja un subrayado deslizante que sobra en este diseño */
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* -----------------------------------------------------------------------------
   5. TARJETA DE PREGUNTA — el corazón de la pantalla
   -------------------------------------------------------------------------- */
.question-card {
    background: var(--mq-surface) !important;
    border: 3px solid #dfe4ff !important;
    border-bottom: 9px solid #c3cbff !important;
    border-radius: var(--mq-radius-lg) !important;
    padding: 30px 28px !important;
    text-align: center !important;
    font-size: var(--mq-fs-lg) !important;
    font-weight: 500 !important;
    line-height: var(--mq-lh) !important;
    color: var(--mq-text) !important;
    box-shadow: var(--mq-shadow-lg) !important;
    margin-bottom: 26px !important;
    position: relative;
    overflow: hidden;
    animation: mq-card-in .4s var(--mq-ease);
}

/* Franja superior de color: identifica el mundo de un vistazo */
.question-card::before {
    content: "";
    position: absolute;
    inset: 0 0 auto 0;
    height: 8px;
    background: linear-gradient(90deg,
        var(--mq-primary) 0%, #38bdf8 33%, #34d399 66%, var(--mq-warning) 100%);
}

@keyframes mq-card-in {
    from { opacity: 0; transform: translateY(14px) scale(.985); }
    to   { opacity: 1; transform: none; }
}

/* Los datos del enunciado en negrita destacan más que el texto corrido */
.question-card strong,
.question-card b {
    color: var(--mq-primary) !important;
    font-weight: 700 !important;
}

.question-badge {
    display: inline-block;
    background: var(--mq-primary-light);
    color: var(--mq-primary);
    font-weight: 700;
    font-size: 14px;
    padding: 6px 18px;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-bottom: 14px;
    border: 2px solid #c7d2fe;
}

/* Resaltado del dato clave: el ojo debe ir ahí primero */
.highlight-text {
    color: var(--mq-primary) !important;
    font-weight: 700 !important;
    background: linear-gradient(180deg, transparent 58%, #dbeafe 58%);
    padding: 2px 8px;
    border-radius: 8px;
    white-space: nowrap;
}

/* Representación visual concreta (barras de fracción, valor posicional).
   Fase "C" del método CPA: Concreto → Pictórico → Abstracto. */
.fraction-visual {
    font-size: 34px;
    letter-spacing: 8px;
    line-height: 1.5;
    margin: 20px auto 6px;
    background: var(--mq-surface-alt);
    padding: 16px 14px;
    border-radius: var(--mq-radius);
    border: 3px dashed var(--mq-border-strong);
    max-width: 100%;
    overflow-x: auto;
}

/* -----------------------------------------------------------------------------
   6. CAJA DE PISTA (CPA) — nunca castiga, siempre enseña
   El error debe leerse como "te ayudo", no como "te equivocaste".
   -------------------------------------------------------------------------- */
.cpa-box {
    background: var(--mq-warning-light) !important;
    border: 3px solid var(--mq-warning-border) !important;
    border-bottom: var(--mq-lift) solid var(--mq-warning) !important;
    border-radius: var(--mq-radius) !important;
    padding: 22px 24px 22px 60px;
    margin: 22px 0;
    font-size: var(--mq-fs-base);
    line-height: var(--mq-lh);
    color: #713f12 !important;
    position: relative;
    box-shadow: var(--mq-shadow);
    animation: mq-card-in .35s var(--mq-ease);
}
.cpa-box::before {
    content: "💡";
    position: absolute;
    left: 18px;
    top: 20px;
    font-size: 26px;
    animation: mq-glow 2s ease-in-out infinite;
}
.cpa-box b { color: #854d0e !important; }

@keyframes mq-glow {
    0%, 100% { transform: scale(1);    opacity: 1;   }
    50%      { transform: scale(1.15); opacity: .85; }
}

/* -----------------------------------------------------------------------------
   7. BOTONES
   Regla: todo lo que se pueda tocar debe PARECER que se puede tocar,
   y debe hundirse al presionarlo (feedback físico inmediato).
   -------------------------------------------------------------------------- */
.stButton > button,
.stFormSubmitButton > button {
    width: 100%;
    min-height: var(--mq-tap);
    border-radius: var(--mq-radius) !important;
    font-family: var(--mq-font) !important;
    font-size: var(--mq-fs-answer) !important;
    font-weight: 700 !important;
    padding: 14px 20px !important;
    background: linear-gradient(180deg, #6366f1 0%, var(--mq-primary) 100%) !important;
    color: #ffffff !important;
    border: 3px solid var(--mq-primary-hover) !important;
    border-bottom: var(--mq-lift) solid var(--mq-primary-dark) !important;
    box-shadow: var(--mq-shadow-lg) !important;
    cursor: pointer;
    transition: transform .1s var(--mq-ease), filter .12s, box-shadow .12s;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    filter: brightness(1.08);
    transform: translateY(-3px);
    box-shadow: 0 20px 34px -12px rgba(79,70,229,.42) !important;
}

/* El "clic jugoso": el botón baja hasta apoyarse en su propio borde */
.stButton > button:active,
.stFormSubmitButton > button:active {
    transform: translateY(var(--mq-lift));
    border-bottom-width: 1px !important;
    box-shadow: none !important;
}

.stButton > button p,
.stButton > button span,
.stFormSubmitButton > button p {
    color: #ffffff !important;
    font-size: var(--mq-fs-answer) !important;
    font-weight: 700 !important;
}

/* Separación entre opciones de respuesta: evita el toque accidental,
   crítico en tablets y en niños con motricidad fina aún en desarrollo. */
[data-testid="column"] .stButton { margin-bottom: 14px; }
[data-testid="column"] { padding: 0 7px !important; }

/* Botón de inicio de sesión: es LA acción de la pantalla, va en verde "adelante" */
.stFormSubmitButton > button {
    background: linear-gradient(180deg, #22c55e 0%, var(--mq-success) 100%) !important;
    border-color: var(--mq-success-dark) !important;
    border-bottom-color: #14532d !important;
    font-size: 28px !important;
}

/* -----------------------------------------------------------------------------
   8. FORMULARIOS Y ENTRADAS
   -------------------------------------------------------------------------- */
.stTextInput input,
.stNumberInput input,
.stSelectbox [data-baseweb="select"] > div {
    font-family: var(--mq-font) !important;
    font-size: 22px !important;
    font-weight: 600 !important;
    min-height: var(--mq-tap) !important;
    border-radius: var(--mq-radius-sm) !important;
    border: 3px solid var(--mq-border) !important;
    background: var(--mq-surface) !important;
    color: var(--mq-text) !important;
    padding: 10px 16px !important;
}
.stTextInput input:focus,
.stNumberInput input:focus {
    border-color: var(--mq-primary) !important;
    box-shadow: 0 0 0 4px var(--mq-primary-light) !important;
}

/* Etiquetas: instrucción corta, siempre visible, nunca solo un placeholder */
.stTextInput label,
.stNumberInput label,
.stSelectbox label {
    font-size: 18px !important;
    font-weight: 600 !important;
    color: var(--mq-text) !important;
    margin-bottom: 6px !important;
}

/* Los +/- del number_input son objetivos táctiles reales */
.stNumberInput button {
    min-width: 46px !important;
    min-height: 46px !important;
    border-radius: 12px !important;
    background: var(--mq-primary-light) !important;
    border: 2px solid #c7d2fe !important;
    color: var(--mq-primary) !important;
}

[data-testid="stForm"] {
    background: var(--mq-surface);
    border: 3px solid var(--mq-border);
    border-bottom: var(--mq-lift) solid var(--mq-border-strong);
    border-radius: var(--mq-radius-lg);
    padding: 30px !important;
    box-shadow: var(--mq-shadow-lg);
}

/* -----------------------------------------------------------------------------
   9. MENSAJES DE ACIERTO / ERROR
   Color + icono + movimiento. Nunca depende únicamente del color.
   -------------------------------------------------------------------------- */
[data-testid="stAlert"] {
    border-radius: var(--mq-radius) !important;
    font-size: var(--mq-fs-lg) !important;
    font-weight: 600 !important;
    padding: 20px 24px !important;
    border: 3px solid transparent !important;
    border-bottom-width: var(--mq-lift) !important;
    box-shadow: var(--mq-shadow);
}
[data-testid="stAlert"] p { font-size: var(--mq-fs-lg) !important; font-weight: 600 !important; }

/* Éxito — celebra y se queda: refuerzo positivo */
[data-testid="stAlert"][data-baseweb="notification"]:has(svg),
.stAlert:has([data-testid="stAlertContentSuccess"]) {
    animation: mq-cheer .55s var(--mq-ease);
}
[data-testid="stAlertContentSuccess"],
div[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) {
    background: var(--mq-success-light) !important;
    border-color: var(--mq-success-border) !important;
    color: #14532d !important;
}

/* Error — atenuado a rosa y con "meneo" corto: señala sin asustar */
[data-testid="stAlertContentError"],
div[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) {
    background: var(--mq-danger-light) !important;
    border-color: var(--mq-danger-border) !important;
    color: #881337 !important;
    animation: mq-shake .4s ease-in-out;
}

[data-testid="stAlertContentWarning"],
div[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) {
    background: var(--mq-warning-light) !important;
    border-color: var(--mq-warning-border) !important;
    color: #713f12 !important;
}

@keyframes mq-cheer {
    0%   { transform: scale(.92); opacity: 0; }
    60%  { transform: scale(1.03); opacity: 1; }
    100% { transform: scale(1); }
}
@keyframes mq-shake {
    0%, 100% { transform: translateX(0); }
    25%      { transform: translateX(-7px); }
    75%      { transform: translateX(7px); }
}

/* Toast de compra */
[data-testid="stToast"] {
    border-radius: var(--mq-radius) !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    border: 3px solid var(--mq-primary) !important;
    background: var(--mq-surface) !important;
}

/* -----------------------------------------------------------------------------
   10. TIENDA Y AVATAR
   -------------------------------------------------------------------------- */
.shop-card {
    background: var(--mq-surface) !important;
    border: 3px solid var(--mq-border) !important;
    border-bottom: var(--mq-lift) solid var(--mq-border-strong) !important;
    border-radius: var(--mq-radius) !important;
    padding: 22px 16px !important;
    text-align: center;
    margin-bottom: 12px;
    box-shadow: var(--mq-shadow);
    transition: transform .16s var(--mq-ease), box-shadow .16s;
}
.shop-card:hover {
    transform: translateY(-5px) rotate(-1deg);
    box-shadow: var(--mq-shadow-lg);
}
.shop-card img {
    width: 64px !important;
    height: 64px !important;
    object-fit: contain;
    filter: drop-shadow(0 5px 8px rgba(23,32,51,.18));
}
.shop-card div:nth-of-type(1) { font-size: 18px !important; font-weight: 700 !important; }
.shop-card div:nth-of-type(2) {
    font-size: 14px !important;
    color: var(--mq-text-soft) !important;
    text-transform: uppercase;
    letter-spacing: .06em;
}

/* -----------------------------------------------------------------------------
   11. VARIOS
   -------------------------------------------------------------------------- */
hr, [data-testid="stDivider"] {
    border: none !important;
    height: 4px !important;
    border-radius: 4px;
    background: linear-gradient(90deg, transparent, var(--mq-border), transparent) !important;
    margin: 26px 0 !important;
}

.stCaption, [data-testid="stCaptionContainer"] p {
    font-size: 17px !important;
    color: var(--mq-text-soft) !important;
}

/* -----------------------------------------------------------------------------
   12. RESPONSIVE — la mayoría de aulas usa tablet en vertical
   -------------------------------------------------------------------------- */
@media (max-width: 780px) {
    :root {
        --mq-fs-base: 17px;
        --mq-fs-lg:   20px;
        --mq-fs-answer: 23px;
    }
    .block-container { padding: 1.2rem .9rem 4rem !important; }
    h1 { font-size: 30px !important; }
    .question-card { padding: 24px 18px !important; border-radius: var(--mq-radius) !important; }
    .stTabs [data-baseweb="tab"] { padding: 10px 14px !important; font-size: 15px !important; }
    .fraction-visual { font-size: 26px; letter-spacing: 5px; }
    /* En pantallas estrechas las 2 columnas de respuestas pasan a 1 */
    [data-testid="column"] { min-width: 100% !important; }
}

/* -----------------------------------------------------------------------------
   13. ACCESIBILIDAD
   -------------------------------------------------------------------------- */

/* Niños con sensibilidad vestibular, TDAH o autismo: sin animación. */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
        scroll-behavior: auto !important;
    }
    .stButton > button:hover,
    .stTabs [data-baseweb="tab"]:hover,
    .shop-card:hover { transform: none !important; }
}

/* Modo alto contraste del sistema operativo */
@media (prefers-contrast: more) {
    :root {
        --mq-text: #000000;
        --mq-text-soft: #1f2937;
        --mq-border: #64748b;
        --mq-border-strong: #334155;
    }
    .question-card, .shop-card, [data-testid="stForm"] { border-width: 4px !important; }
}

/* La app se fuerza en claro: el tema oscuro de Streamlit rompería
   los contrastes calculados arriba y no aporta nada en un aula. */
@media (prefers-color-scheme: dark) {
    .stApp { background-color: var(--mq-bg) !important; color: var(--mq-text) !important; }
    .question-card, .shop-card, .hud-card, [data-testid="stForm"] {
        background: var(--mq-surface) !important;
        color: var(--mq-text) !important;
    }
}

/* -----------------------------------------------------------------------------
   14. EXPLICACIÓN CPA (Concreto → Pictórico → Abstracto)
   La pista no da la respuesta: construye el concepto y la respuesta cierra.
   Ver cpa.py para el contenido pedagógico.
   -------------------------------------------------------------------------- */

/* Cada paso numerado del razonamiento */
.cpa-step {
    margin: 0 0 16px;
    padding: 0 0 14px;
    border-bottom: 2px dashed rgba(180, 132, 20, .25);
}
.cpa-step:last-of-type { border-bottom: none; padding-bottom: 4px; }

.cpa-step-label {
    display: inline-block;
    background: var(--mq-warning);
    color: #fff;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: .08em;
    padding: 4px 12px;
    border-radius: 999px;
    margin-bottom: 8px;
    text-transform: uppercase;
}
.cpa-step-body { font-size: 17px; line-height: 1.6; }

/* La respuesta: separada, al final, nunca es lo primero que se lee */
.cpa-result {
    margin-top: 14px;
    padding: 14px 18px;
    background: var(--mq-surface);
    border: 3px solid var(--mq-warning-border);
    border-radius: var(--mq-radius-sm);
    font-size: 21px;
    font-weight: 700;
    text-align: center;
    color: #854d0e;
}

/* --- Rejilla de multiplicación / división ---
   Una fila por grupo. El número de fila a la izquierda y el acumulado a la
   derecha son lo que convierte el dibujo en explicación: el niño ve el
   conteo salteado construirse (5, 10, 15...). */
.cpa-grid {
    margin: 12px 0;
    background: #fff;
    border: 2px solid var(--mq-warning-border);
    border-radius: var(--mq-radius-sm);
    padding: 12px 14px;
    overflow-x: auto;
}
.cpa-row {
    display: flex;
    align-items: center;
    gap: 10px;
    white-space: nowrap;
    padding: 2px 0;
}
.cpa-blocks { display: inline-flex; gap: 3px; }

/* Cada bloque es un cuadro real, no un carácter suelto */
.cpa-blk {
    font-size: 22px;
    line-height: 1;
    font-style: normal;
}
.cpa-grid.sm .cpa-blk { font-size: 16px; }
.cpa-grid.sm .cpa-blocks { gap: 2px; }

/* Número de grupo (1, 2, 3...) */
.cpa-row-n {
    flex-shrink: 0;
    width: 24px;
    font-size: 13px;
    font-weight: 700;
    color: #b45309;
    text-align: right;
}
.cpa-row-n::after { content: "·"; margin-left: 3px; }

/* Acumulado: la columna que enseña a contar de N en N */
.cpa-count {
    flex-shrink: 0;
    margin-left: auto;
    padding-left: 10px;
    font-size: 15px;
    font-weight: 700;
    color: #92400e;
}
.cpa-count::before {
    content: "";
    display: inline-block;
    width: 14px;
    height: 2px;
    background: #fcd34d;
    vertical-align: middle;
    margin-right: 7px;
}
.cpa-row:last-child .cpa-count {
    background: var(--mq-warning);
    color: #fff;
    border-radius: 999px;
    padding: 2px 12px;
    margin-left: auto;
}
.cpa-row:last-child .cpa-count::before { display: none; }

/* --- Figuras geométricas dibujadas --- */
.cpa-figure { margin: 12px 0; text-align: center; }
.cpa-fig-top,
.cpa-fig-side {
    font-size: 13px;
    font-weight: 700;
    color: #92400e;
    text-transform: uppercase;
    letter-spacing: .05em;
}
.cpa-fig-top { margin-bottom: 6px; }
.cpa-fig-side { margin-top: 6px; }
.cpa-figure .cpa-grid { display: inline-block; text-align: left; }
.cpa-figure .cpa-row { gap: 0; }

.cpa-svg {
    width: 100%;
    max-width: 240px;
    height: auto;
    margin: 10px auto;
    display: block;
}
.cpa-svg-t {
    font-family: var(--mq-font);
    font-size: 19px;
    font-weight: 700;
    fill: #1e3a8a;
    text-anchor: middle;
}

/* --- Barra de modelo (método de barras, estilo Singapur) --- */
.cpa-bar { margin: 10px 0; }
.cpa-bar-whole {
    display: block;
    background: linear-gradient(180deg, #93c5fd, #60a5fa);
    color: #0b2e5c;
    font-weight: 700;
    text-align: center;
    padding: 12px;
    border-radius: 12px;
    border: 2px solid #3b82f6;
}

/* --- Figuras geométricas --- */
.cpa-shape { text-align: center; margin: 10px 0; font-weight: 700; }
.cpa-shape-top { color: #92400e; font-size: 15px; }
.cpa-shape-mid {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    color: #92400e;
    font-size: 15px;
}
.cpa-shape-box { font-size: 42px; line-height: 1; }
.cpa-tri { text-align: center; font-size: 40px; line-height: 1.2; }
.cpa-tri span { font-size: 15px; font-weight: 700; color: #92400e; }

/* --- Fracciones: barra de partes iguales --- */
.cpa-frac-bar {
    display: flex;
    gap: 3px;
    margin: 12px 0 8px;
    height: 46px;
}
.cpa-frac-bar span {
    flex: 1;
    border-radius: 8px;
    border: 2px solid #86efac;
}
.cpa-frac-on  { background: linear-gradient(180deg, #4ade80, #22c55e); }
.cpa-frac-off { background: repeating-linear-gradient(45deg, #fff, #fff 5px, #f1f5f9 5px, #f1f5f9 10px); }

.cpa-frac-legend { font-size: 14px; color: #713f12; }
.cpa-frac-legend span {
    display: inline-block;
    width: 15px; height: 15px;
    border-radius: 4px;
    vertical-align: -2px;
    border: 2px solid #86efac;
}

/* La fracción escrita como fracción de verdad, no como "3/4" */
.cpa-frac-math {
    display: inline-block;
    text-align: center;
    margin: 6px 14px 10px 0;
    vertical-align: middle;
}
.cpa-frac-math .cpa-num,
.cpa-frac-math .cpa-den {
    display: block;
    font-size: 26px;
    font-weight: 700;
    color: #854d0e;
    line-height: 1.1;
}
.cpa-frac-math .cpa-line {
    display: block;
    height: 3px;
    background: #854d0e;
    border-radius: 2px;
    margin: 3px 0;
}

/* --- Decimales: tabla de valor posicional --- */
.cpa-place {
    display: flex;
    align-items: flex-end;
    justify-content: center;
    gap: 8px;
    margin: 12px 0;
    flex-wrap: wrap;
}
.cpa-place > div { text-align: center; }
.cpa-place-h {
    display: block;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .05em;
    color: #92400e;
    margin-bottom: 4px;
}
.cpa-place-v {
    display: block;
    font-size: 30px;
    font-weight: 700;
    color: #854d0e;
    background: #fff;
    border: 3px solid var(--mq-warning-border);
    border-radius: 12px;
    padding: 6px 18px;
    min-width: 54px;
}
.cpa-place-dot { font-size: 34px; font-weight: 700; color: #b45309; padding-bottom: 4px; }

/* --- Decimales: comparación A vs B --- */
.cpa-compare {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
    margin: 12px 0;
}
.cpa-comp-item {
    background: #fff;
    border: 3px solid var(--mq-warning-border);
    border-radius: var(--mq-radius-sm);
    padding: 10px 18px;
    text-align: center;
    min-width: 90px;
}
.cpa-comp-item b { display: block; font-size: 13px; color: #92400e; }
.cpa-comp-item span { font-size: 26px; font-weight: 700; color: #854d0e; }
.cpa-comp-vs { font-weight: 700; color: #b45309; font-size: 15px; }

/* --- Decimales: cadena de conversión --- */
.cpa-convert {
    text-align: center;
    font-size: 18px;
    font-weight: 700;
    color: #92400e;
    margin: 12px 0;
    line-height: 2;
}
.cpa-convert span {
    background: #fff;
    border: 2px solid var(--mq-warning-border);
    border-radius: 10px;
    padding: 5px 12px;
    display: inline-block;
}
.cpa-convert-out { background: var(--mq-warning) !important; color: #fff !important; }

@media (max-width: 780px) {
    .cpa-grid { font-size: 17px; letter-spacing: 1px; }
    .cpa-step-body { font-size: 16px; }
    .cpa-result { font-size: 19px; }
    .cpa-place-v { font-size: 24px; padding: 5px 12px; min-width: 44px; }
}

/* -----------------------------------------------------------------------------
   15. LEYENDAS DE LOS DIBUJOS CPA
   Un dibujo sin rótulos es un jeroglífico: hay que decir qué es cada columna.
   -------------------------------------------------------------------------- */

/* Cabecera de la rejilla de multiplicación */
.cpa-grid-head {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 8px;
    margin-bottom: 8px;
    border-bottom: 2px solid #fde68a;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .05em;
    color: #b45309;
    white-space: nowrap;
}
.cpa-h-n { width: 24px; text-align: right; flex-shrink: 0; }
.cpa-h-b { flex: 1; }
.cpa-h-c { margin-left: auto; flex-shrink: 0; }

/* --- División dibujada como REPARTO en grupos --- */
.cpa-share {
    margin: 12px 0;
    background: #fff;
    border: 2px solid var(--mq-warning-border);
    border-radius: var(--mq-radius-sm);
    padding: 12px 14px;
    overflow-x: auto;
}
.cpa-share-head {
    font-size: 13px;
    font-weight: 700;
    color: #b45309;
    padding-bottom: 8px;
    margin-bottom: 8px;
    border-bottom: 2px solid #fde68a;
    text-align: center;
}

/* Cada grupo es una caja rotulada: eso es lo que faltaba */
.cpa-share-row {
    display: flex;
    align-items: center;
    gap: 10px;
    white-space: nowrap;
    padding: 5px 8px;
    margin-bottom: 5px;
    background: #fffbeb;
    border: 2px dashed #fcd34d;
    border-radius: 10px;
}
.cpa-share-row:last-child { margin-bottom: 0; }

.cpa-share-tag {
    flex-shrink: 0;
    font-size: 12px;
    font-weight: 700;
    color: #92400e;
    background: #fef3c7;
    border-radius: 999px;
    padding: 3px 10px;
    min-width: 62px;
    text-align: center;
}
.cpa-share-get {
    flex-shrink: 0;
    margin-left: auto;
    padding-left: 10px;
    font-size: 13px;
    font-weight: 700;
    color: #92400e;
}
.cpa-share.sm .cpa-blk { font-size: 16px; }
.cpa-share.sm .cpa-blocks { gap: 2px; }

@media (max-width: 780px) {
    .cpa-grid-head, .cpa-share-head { font-size: 10px; }
    .cpa-share-tag { min-width: 52px; font-size: 11px; }
    .cpa-share-get { font-size: 11px; }
}

</style>
""", unsafe_allow_html=True)

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

    # Las opciones se barajan AQUI y se guardan en el estado.
    # Si se barajaran en el render, cada rerun cambiaria la key de los botones
    # y el clic del nino se perderia (la app parecia bloquearse).
    c = st.session_state.correcta_op
    opciones = list({c, c + 2, max(1, c - 1), c + 3})
    random.shuffle(opciones)
    st.session_state.opciones_op = opciones

    st.session_state.mostrar_pista_op = False
    st.session_state.reto_op_id = time.time()


def nuevo_reto_fracciones():
    den = random.choice([2, 3, 4, 5, 6, 8, 10])
    num = random.randint(1, den - 1)
    st.session_state.denominador = den
    st.session_state.numerador = num
    correcta = f"{num}/{den}"
    opciones = list({correcta, f"{den - num}/{den}",
                     f"{num}/{den + 1 if den < 8 else den - 1}"})
    random.shuffle(opciones)
    st.session_state.opciones_frac = opciones

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
        st.markdown(f'<div class="cpa-box"><b>{t["cpa_title"]}</b>{cpa.explicar_problema(pdata, lang)}</div>', unsafe_allow_html=True)

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
        st.markdown(f'<div class="cpa-box"><b>{t["cpa_title"]}</b>{cpa.explicar_geometria(gdata, lang)}</div>', unsafe_allow_html=True)

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
        st.markdown(f'<div class="cpa-box"><b>{t["cpa_title"]}</b>{cpa.explicar_operacion(tipo_op, n1, n2, correcta_o, lang)}</div>', unsafe_allow_html=True)

    opciones_o = st.session_state.opciones_op

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

    if st.session_state.mostrar_pista_frac:
        st.markdown(f'<div class="cpa-box"><b>{t["cpa_title"]}</b>{cpa.explicar_fraccion(num, den, lang)}</div>', unsafe_allow_html=True)

    opciones_f = st.session_state.opciones_frac

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
        st.markdown(f'<div class="cpa-box"><b>{t["cpa_title"]}</b>{cpa.explicar_decimal(tipo_d, d_data, st.session_state.dec_correcta, lang)}</div>', unsafe_allow_html=True)

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