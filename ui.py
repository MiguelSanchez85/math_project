"""
Carga de la hoja de estilos de Math Quest.

Uso en app.py — reemplaza todo el bloque `st.markdown(<style>...</style>)`
de la sección 2 por estas dos líneas:

    from ui import cargar_estilos
    cargar_estilos()

(colocarlas justo después de `st.set_page_config(...)`)
"""

from pathlib import Path

import streamlit as st

RUTA_CSS = Path(__file__).parent / "style.css"


@st.cache_data(show_spinner=False)
def _leer_css(ruta: str, mtime: float) -> str:
    """Lee el CSS. `mtime` entra en la firma para invalidar la caché al editarlo."""
    return Path(ruta).read_text(encoding="utf-8")


def cargar_estilos(ruta: Path = RUTA_CSS) -> None:
    """Inyecta style.css en la página. Si falta el archivo, avisa y sigue."""
    if not ruta.exists():
        st.warning(f"No se encontró la hoja de estilos: {ruta.name}")
        return

    css = _leer_css(str(ruta), ruta.stat().st_mtime)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
