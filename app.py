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
            else:
                st.error("Contraseña incorrecta")
        return False
    return True

# --- MOTOR GRÁFICO (RESTAURADO) ---
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
        # Nombres exactos de tus archivos en assets/fonts
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
        
        # 2. Caja lila del tema (CENTRAL)
        self.c.setFillColor(HexColor("#E8E2E8"))
        self.c.roundRect(362, self.PAGE_H-65, 300, 32, 6, fill=1, stroke=0)
        
        self.c.setFont(self.font_main, 18); self.c.setFillColor(HexColor("#3D3D3D"))
        self.c.drawCentredString(512, self.PAGE_H-58, self.tema.upper())
        
        # 3. Marca de agua derecha
        self.c.drawRightString(self.PAGE_W-50, self.PAGE_H-58, "OPOSITA EN TIEMPO EXPRESS")

    def check_espacio((alto)):
        if self.y < (alto + 60):
            self.c.showPage()
            self.dibujar_plantilla()
            self.y = self.PAGE_H - 140

    def add_texto(self, texto, bullet=False):
        # Wrapping: divide el texto si es muy largo
        ancho_max = 820 if bullet else 880
        x_inicio = 95 if bullet else 70
        
        lineas = simpleSplit(texto, self.font_main, 15, ancho_max)
        
        # Comprobar si caben todas las líneas de este bloque
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
            self.c.drawString(x_inicio, self.y, linea)
            self.y -= 25

    def finalizar(self):
        self.c.save()

# --- LECTORES ---
def leer_archivo(f):
    if f.name.endswith('.docx'): return "\n".join([p.text for p in docx.Document(f).paragraphs])
    if f.name.endswith('.pdf'): return "\n".join([p.extract_text() for p in PyPDF2.PdfReader(f).pages])
    return ""

# --- INTERFAZ ---
if check_password():
    st.title("📝 OTE Studio PRO")
    
    with st.sidebar:
        tema_n = st.text_input("Nombre del Tema", "Tema 1 IASS")
        metodo = st.radio("Entrada:", ["Pegar Texto", "Subir Archivo"])

    contenido = ""
    if metodo == "Subir Archivo":
        f = st.file_uploader("Sube tu Word o PDF", type=['docx', 'pdf'])
        if f: contenido = leer_archivo(f)
    else:
        contenido = st.text_area("Pega tus apuntes:", height=300)

    if st.button("✨ Generar PDF Bonito"):
        if contenido:
            buf = io.BytesIO()
            gen = OTEGenerator(buf, tema_n)
            for parrafo in contenido.split('\n'):
                linea = parrafo.strip()
                if not linea: continue
                
                # Usamos 'gen.y' en lugar de 'self.y'
                if linea.startswith('-'):
                    gen.add_texto(linea[1:].strip(), bullet=True)
                else:
                    gen.add_texto(linea)
            
            gen.finalizar()
            st.success("¡PDF generado!")
            st.download_button("⬇️ Descargar PDF", buf.getvalue(), f"{tema_n}.pdf")
