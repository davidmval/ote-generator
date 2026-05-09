import streamlit as st
import os, io
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import docx
from odf import text, teletype
from odf.opendocument import load
import PyPDF2

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="OTE Studio Cloud", layout="wide")

# --- FUNCIÓN DE CONTRASEÑA ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔒 Acceso Privado OTE")
        pwd = st.text_input("Introduce la contraseña del equipo:", type="password")
        if st.button("Entrar"):
            if pwd == st.secrets["password"]:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
        return False
    return True

# --- LÓGICA DE LA APP ---
if check_password():
    st.title("📝 OTE Studio: Generador de Apuntes")
    
    with st.sidebar:
        st.header("Configuración")
        nombre_tema = st.text_input("Nombre del Tema", "Tema 1 IASS")
        # Aseguramos que la lista de opciones nunca sea nula
        metodo = st.radio("Método de entrada:", ["Subir Archivo", "Pegar Texto"])

    # Espacio para el contenido
    contenido = ""
    
    if metodo == "Subir Archivo":
        f = st.file_uploader("Sube tu documento (docx, odt, pdf)", type=['docx', 'odt', 'pdf'])
        if f:
            # Aquí irían tus funciones de lectura (read_docx, read_pdf...)
            st.success("Archivo cargado con éxito")
            # Simulación de contenido para prueba
            contenido = "Contenido extraído del archivo..." 
    else:
        contenido = st.text_area("Pega aquí el texto de tus apuntes:", height=400)

    if st.button("✨ Generar mi PDF Bonito"):
        if contenido and nombre_tema:
            st.info(f"Generando PDF para: {nombre_tema}...")
            # Aquí se llama a tu clase OTEGenerator con la iconografía
        else:
            st.warning("Por favor, introduce el contenido antes de generar.")
