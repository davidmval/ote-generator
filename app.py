import streamlit as st
import os, io
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
# ... (resto de importaciones de docx, pdf2, etc.)

# --- FUNCIÓN DE SEGURIDAD ---
def check_password():
    """Devuelve True si el usuario introdujo la contraseña correcta."""
    def password_entered():
        # Compara con la contraseña guardada en los Secretos de la App
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # No guardar la contraseña en sesión
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Primera vez que entra
        st.text_input("Introduce la contraseña de equipo OTE", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Contraseña incorrecta
        st.text_input("Contraseña incorrecta. Inténtalo de nuevo", type="password", on_change=password_entered, key="password")
        st.error("😕 Acceso denegado")
        return False
    else:
        # Contraseña correcta
        return True

# --- LÓGICA PRINCIPAL ---
if check_password():
    st.title("📝 OTE Studio: Generador de Apuntes Privado")
    
    # Aquí va todo el código anterior (subida de archivos, generación de PDF, etc.)
    # El generador respetará la plantilla de lila central y fondo de puntos
    # y los iconos de corazones y cajas con washi tape.
    
    nombre_tema = st.text_input("Nombre del Tema", "Tema 1 IASS")
    # ... resto de la app ...