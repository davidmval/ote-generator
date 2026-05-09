import streamlit as st
import os, io, docx, PyPDF2
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

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

# --- MOTOR GRÁFICO OTE ---
class OTEGenerator:
    def __init__(self, buffer, tema):
        self.buffer = buffer
        self.tema = tema
        self.PAGE_W, self.PAGE_H = 1024, 704
        self.y = self.PAGE_H - 140
        self.c = canvas.Canvas(self.buffer, pagesize=(self.PAGE_W, self.PAGE_H))
        self.font_name = self.registrar_fuentes()
        self.dibujar_base()

    def registrar_fuentes(self):
        ruta = "assets/fonts/PatrickHand.ttf"
        if os.path.exists(ruta):
            try:
                pdfmetrics.registerFont(TTFont('PatrickHand', ruta))
                return 'PatrickHand'
            except: pass
        return 'Helvetica'

    def dibujar_base(self):
        # 1. Fondo de puntos grises
        self.c.setFillColor(white); self.c.rect(0,0,self.PAGE_W,self.PAGE_H,fill=1,stroke=0)
        self.c.setFillColor(HexColor("#D1D1D1"))
        for x in range(30, 1010, 35):
            for y in range(30, 680, 35):
                self.c.circle(x, y, 0.7, fill=1, stroke=0)
        
        # 2. Caja lila del tema (CENTRAL)
        self.c.setFillColor(HexColor("#E8E2E8"))
        self.c.roundRect(362, self.PAGE_H-65, 300, 32, 6, fill=1, stroke=0)
        self.c.setFont(self.font_name, 18); self.c.setFillColor(HexColor("#3D3D3D"))
        self.c.drawCentredString(512, self.PAGE_H-58, self.tema.upper())
        
        # 3. Logo y marca lateral
        self.c.drawRightString(self.PAGE_W-50, self.PAGE_H-58, "OPOSITA EN TIEMPO EXPRESS")
        logo = "assets/img/template_img_1.png"
        if os.path.exists(logo):
            self.c.drawImage(logo, 930, self.PAGE_H-110, 60, 52, mask='auto')

    def add_parrafo(self, texto, es_bullet=False):
        # Sistema de ajuste automático de texto (Wrapping)
        ancho = 820 if es_bullet else 880
        x_inicio = 95 if es_bullet else 70
        lineas = simpleSplit(texto, self.font_name, 15, ancho)
        
        if self.y - (len(lineas) * 25) < 60:
            self.c.showPage()
            self.dibujar_base()
            self.y = self.PAGE_H - 140

        if es_bullet:
            self.c.setFillColor(HexColor("#E8B4B8")) # Corazón rosa
            self.c.circle(80, self.y + 5, 4, fill=1, stroke=0)
            self.c.setFillColor(HexColor("#3D3D3D"))

        self.c.setFont(self.font_name, 15)
        for linea in lineas:
            self.c.drawString(x_inicio, self.y, linea)
            self.y -= 25

    def guardar(self):
        self.c.save()

# --- INTERFAZ ---
if check_password():
    st.title("📝 OTE Studio PRO")
    
    with st.sidebar:
        tema_n = st.text_input("Nombre del Tema", "Tema 1 IASS")
        metodo = st.radio("Entrada de contenido:", ["Pegar Texto", "Subir Archivo"])

    contenido = ""
    if metodo == "Subir Archivo":
        f = st.file_uploader("Documento (docx, pdf)", type=['docx', 'pdf'])
        if f:
            if f.name.endswith('.docx'): contenido = "\n".join([p.text for p in docx.Document(f).paragraphs])
            else: contenido = "\n".join([p.extract_text() for p in PyPDF2.PdfReader(f).pages])
    else:
        contenido = st.text_area("Pega tus apuntes:", height=300)

    if st.button("✨ Generar PDF OTE"):
        if contenido:
            buf = io.BytesIO()
            pdf = OTEGenerator(buf, tema_n)
            for bloque in contenido.split('\n'):
                linea = bloque.strip()
                if not linea: continue
                # Detecta si es una lista para poner el corazón
                if linea.startswith('-'):
                    pdf.add_parrafo(linea[1:].strip(), es_bullet=True)
                else:
                    pdf.add_parrafo(linea)
            pdf.guardar()
            st.success("¡Apuntes listos con estilo OTE!")
            st.download_button("⬇️ Descargar PDF", buf.getvalue(), f"{tema_n}.pdf")
