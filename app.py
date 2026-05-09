import streamlit as st
import os, io, docx, PyPDF2
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
from odf import text, teletype
from odf.opendocument import load

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="OTE Studio PRO", layout="centered")

# --- SEGURIDAD ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        st.title("🔒 Acceso OTE")
        pwd = st.text_input("Contraseña del equipo:", type="password")
        if st.button("Entrar"):
            if pwd == st.secrets["password"]:
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Clave incorrecta")
        return False
    return True

# --- MOTOR GRÁFICO ---
class OTEGenerator:
    def __init__(self, buffer, tema):
        self.buffer = buffer
        self.tema = tema
        self.PAGE_W, self.PAGE_H = 1024, 704
        self.y = self.PAGE_H - 140
        self.c = canvas.Canvas(self.buffer, pagesize=(self.PAGE_W, self.PAGE_H))
        self.font_main = self.cargar_fuentes()
        self.dibujar_plantilla()

    def cargar_fuentes(self):
        f_path = "assets/fonts/PatrickHand.ttf"
        try:
            if os.path.exists(f_path):
                pdfmetrics.registerFont(TTFont('PatrickHand', f_path))
                return 'PatrickHand'
            return 'Helvetica'
        except: return 'Helvetica'

    def dibujar_plantilla(self):
        # 1. Fondo de puntos grises
        self.c.setFillColor(white); self.c.rect(0,0,self.PAGE_W,self.PAGE_H,fill=1,stroke=0)
        self.c.setFillColor(HexColor("#D1D1D1"))
        for x in range(30, 1010, 35):
            for y in range(30, 680, 35):
                self.c.circle(x, y, 0.7, fill=1, stroke=0)
        
        # 2. Caja lila del tema central
        self.c.setFillColor(HexColor("#E8E2E8"))
        self.c.roundRect(362, self.PAGE_H-65, 300, 32, 6, fill=1, stroke=0)
        self.c.setFont(self.font_main, 18); self.c.setFillColor(HexColor("#3D3D3D"))
        self.c.drawCentredString(512, self.PAGE_H-58, self.tema.upper())
        
        # 3. Marca lateral
        self.c.drawRightString(self.PAGE_W-50, self.PAGE_H-58, "OPOSITA EN TIEMPO EXPRESS")
        
        # 4. Logo
        logo = "assets/img/template_img_1.png"
        if os.path.exists(logo):
            self.c.drawImage(logo, 930, self.PAGE_H-110, 60, 52, mask='auto')

    def add_texto(self, texto, bullet=False):
        # Word Wrapping automático
        x_pos = 95 if bullet else 70
        ancho = 820 if bullet else 880
        lineas = simpleSplit(texto, self.font_main, 15, ancho)
        
        if self.y - (len(lineas) * 25) < 60:
            self.c.showPage()
            self.dibujar_plantilla()
            self.y = self.PAGE_H - 140

        if bullet:
            self.c.setFillColor(HexColor("#E8B4B8")) # Corazón rosa
            self.c.circle(80, self.y + 5, 4, fill=1, stroke=0)
            self.c.setFillColor(HexColor("#3D3D3D"))

        self.c.setFont(self.font_main, 15)
        for linea in lineas:
            self.c.drawString(x_pos, self.y, linea)
            self.y -= 25

    def finalizar(self):
        self.c.save()

# --- LECTORES DE ARCHIVOS ---
def leer_archivo(f):
    if f.name.endswith('.docx'):
        return "\n".join([p.text for p in docx.Document(f).paragraphs])
    if f.name.endswith('.pdf'):
        return "\n".join([page.extract_text() for page in PyPDF2.PdfReader(f).pages])
    if f.name.endswith('.odt'):
        doc = load(f)
        return "\n".join([teletype.get_content(p) for p in doc.getElementsByType(text.P)])
    return ""

# --- INTERFAZ ---
if check_password():
    st.title("📝 OTE Studio PRO")
    
    with st.sidebar:
        tema_n = st.text_input("Nombre del Tema:", "Tema 1 IASS")
        metodo = st.radio("Entrada:", ["Subir Archivo", "Pegar Texto"])

    contenido_final = ""
    if metodo == "Subir Archivo":
        archivo = st.file_uploader("Sube Word, PDF u ODT", type=['docx', 'pdf', 'odt'])
        if archivo: contenido_final = leer_archivo(archivo)
    else:
        contenido_final = st.text_area("Pega tus apuntes:", height=350)

    if st.button("✨ Generar PDF OTE"):
        if contenido_final:
            buf = io.BytesIO()
            pdf = OTEGenerator(buf, tema_n)
            for parrafo in contenido_final.split('\n'):
                linea = parrafo.strip()
                if linea:
                    if linea.startswith('-'):
                        pdf.add_texto(linea[1:].strip(), bullet=True)
                    else:
                        pdf.add_texto(linea)
            pdf.finalizar()
            st.download_button("⬇️ Descargar mis Apuntes", buf.getvalue(), f"{tema_n}.pdf")
        else:
            st.warning("⚠️ No hay contenido para procesar.")
