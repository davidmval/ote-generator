import streamlit as st
import os, io, docx, PyPDF2
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="OTE Studio PRO", layout="centered")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        st.title("🔒 Acceso OTE")
        pwd = st.text_input("Contraseña:", type="password")
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
        self.y = self.PAGE_H - 135
        self.c = canvas.Canvas(self.buffer, pagesize=(self.PAGE_W, self.PAGE_H))
        self.font_name = self.cargar_fuentes()
        self.dibujar_plantilla()

    def cargar_fuentes(self):
        f_path = os.path.join("assets", "fonts", "PatrickHand.ttf")
        if os.path.exists(f_path):
            pdfmetrics.registerFont(TTFont('PatrickHand', f_path))
            return 'PatrickHand'
        return 'Helvetica'

    def dibujar_plantilla(self):
        # 1. Fondo de puntos grises
        self.c.setFillColor(white); self.c.rect(0,0,self.PAGE_W,self.PAGE_H,fill=1,stroke=0)
        self.c.setFillColor(HexColor("#D1D1D1"))
        for x in range(30, 1010, 35):
            for y in range(30, 680, 35):
                self.c.circle(x, y, 0.7, fill=1, stroke=0)
        # 2. Caja lila del tema (CENTRAL)
        self.c.setFillColor(HexColor("#E8E2E8"))
        self.c.roundRect(362, self.PAGE_H-65, 300, 32, 6, fill=1, stroke=0)
        self.c.setFont(self.font_name, 17); self.c.setFillColor(HexColor("#3D3D3D"))
        self.c.drawCentredString(512, self.PAGE_H-58, self.tema.upper())
        self.c.drawRightString(self.PAGE_W-50, self.PAGE_H-58, "OPOSITA EN TIEMPO EXPRESS")

    def add_texto(self, texto, bullet=False):
        # Evitar que el texto se salga de la página
        ancho_max = 820 if bullet else 880
        x_inicio = 95 if bullet else 70
        lineas = simpleSplit(texto, self.font_name, 15, ancho_max)
        
        if self.y - (len(lineas) * 25) < 60:
            self.c.showPage()
            self.dibujar_plantilla()
            self.y = self.PAGE_H - 135

        if bullet:
            self.c.setFillColor(HexColor("#E8B4B8")) # Corazón rosa
            self.c.circle(80, self.y + 5, 4, fill=1, stroke=0)
            self.c.setFillColor(HexColor("#3D3D3D"))

        self.c.setFont(self.font_name, 15)
        for linea in lineas:
            self.c.drawString(x_inicio, self.y, linea)
            self.y -= 25

    def finalizar(self):
        self.c.save()

# --- INTERFAZ ---
if check_password():
    st.title("📝 OTE Studio PRO")
    
    with st.sidebar:
        tema_n = st.text_input("Nombre del Tema", "Tema 1 IASS")
        metodo = st.radio("Entrada:", ["Pegar Texto", "Subir Word"])

    contenido = ""
    if metodo == "Subir Word":
        f = st.file_uploader("Sube tu Word (.docx)", type=['docx'])
        if f: contenido = "\n".join([p.text for p in docx.Document(f).paragraphs])
    else:
        contenido = st.text_area("Pega tus apuntes:", height=300)

    if st.button("✨ Generar PDF Bonito"):
        if contenido:
            buf = io.BytesIO()
            gen = OTEGenerator(buf, tema_n)
            for parrafo in contenido.split('\n'):
                linea = parrafo.strip()
                if not linea: continue
                if linea.startswith('-'):
                    gen.add_texto(linea[1:].strip(), bullet=True)
                else:
                    gen.add_texto(linea)
            gen.finalizar()
            st.success("¡PDF generado!")
            st.download_button("⬇️ Descargar PDF", buf.getvalue(), f"{tema_n}.pdf")
