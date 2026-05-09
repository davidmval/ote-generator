import streamlit as st
import os, io, docx, PyPDF2
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

# --- CONFIGURACIÓN DE COLORES (Según tu iconografía) ---
C = {
    'lila_header': HexColor("#E8E2E8"), # Color de la caja central
    'puntos': HexColor("#D1D1D1"),      # Gris de los puntos de fondo
    'texto': HexColor("#3D3D3D"),
    'rosa_corazon': HexColor("#E8B4B8") # Rosa para los corazones
}

# --- FUNCIÓN DE SEGURIDAD ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        st.title("🔒 Acceso Privado OTE")
        pwd = st.text_input("Contraseña:", type="password")
        if st.button("Entrar"):
            if pwd == st.secrets["password"]:
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Contraseña incorrecta")
        return False
    return True

# --- MOTOR DE GENERACIÓN PDF ---
class OTEGenerator:
    def __init__(self, buffer, tema):
        self.buffer = buffer
        self.tema = tema
        self.PAGE_W, self.PAGE_H = 1024, 704
        self.y = self.PAGE_H - 140
        self.c = canvas.Canvas(self.buffer, pagesize=(self.PAGE_W, self.PAGE_H))
        self.font_name = self.cargar_fuentes()
        self.dibujar_plantilla()

    def cargar_fuentes(self):
        # Usamos rutas absolutas para que Streamlit Cloud no se pierda
        base_path = os.path.dirname(__file__)
        f_path = os.path.join(base_path, "assets", "fonts", "PatrickHand.ttf")
        
        if os.path.exists(f_path):
            try:
                pdfmetrics.registerFont(TTFont('PatrickHand', f_path))
                return 'PatrickHand'
            except: pass
        return 'Helvetica'

    def dibujar_plantilla(self):
        # 1. Dibujar fondo de puntos exacto
        self.c.setFillColor(white); self.c.rect(0,0,self.PAGE_W,self.PAGE_H,fill=1,stroke=0)
        self.c.setFillColor(C['puntos'])
        for x in range(30, 1010, 35):
            for y in range(30, 680, 35):
                self.c.circle(x, y, 0.7, fill=1, stroke=0)
        
        # 2. Dibujar Caja Lila Central
        self.c.setFillColor(C['lila_header'])
        self.c.roundRect(362, self.PAGE_H-65, 300, 32, 6, fill=1, stroke=0)
        
        # 3. Títulos y Marca
        f_name = self.font_name
        self.c.setFont(f_name, 17); self.c.setFillColor(C['texto'])
        self.c.drawCentredString(512, self.PAGE_H-58, self.tema.upper())
        self.c.drawRightString(self.PAGE_W-50, self.PAGE_H-58, "OPOSITA EN TIEMPO EXPRESS")

    def add_parrafo(self, texto, es_bullet=False):
        # Ajuste de línea automático (Wrapping)
        x_start = 95 if es_bullet else 70
        ancho_max = 820 if es_bullet else 880
        lineas = simpleSplit(texto, self.font_name, 15, ancho_max)
        
        if self.y - (len(lineas) * 25) < 60:
            self.c.showPage()
            self.dibujar_plantilla()
            self.y = self.PAGE_H - 140

        if es_bullet:
            self.c.setFillColor(C['rosa_corazon'])
            self.c.circle(80, self.y + 5, 4, fill=1, stroke=0) # Corazón rosa
            self.c.setFillColor(C['texto'])

        self.c.setFont(self.font_name, 15)
        for linea in lineas:
            self.c.drawString(x_start, self.y, linea)
            self.y -= 25

    def guardar(self):
        self.c.save()

# --- INTERFAZ STREAMLIT ---
if check_password():
    st.title("📝 OTE Studio PRO")
    
    # Comprobar recursos para avisar al usuario
    if not os.path.exists("assets/fonts/PatrickHand.ttf"):
        st.warning("⚠️ No se encuentra 'PatrickHand.ttf' en assets/fonts/. Se usará una fuente estándar.")

    with st.sidebar:
        tema_n = st.text_input("Nombre del Tema", "Tema 1 IASS")
        metodo = st.radio("Entrada de contenido:", ["Pegar Texto", "Subir Word"])

    contenido = ""
    if metodo == "Subir Word":
        f = st.file_uploader("Documento .docx", type=['docx'])
        if f: 
            doc = docx.Document(f)
            contenido = "\n".join([p.text for p in doc.paragraphs])
    else:
        contenido = st.text_area("Pega tus apuntes:", height=300)

    if st.button("✨ Generar PDF Bonito"):
        if contenido:
            buf = io.BytesIO()
            pdf = OTEGenerator(buf, tema_n)
            for bloque in contenido.split('\n'):
                linea = bloque.strip()
                if not linea: continue
                # Detectar si es una lista para poner el corazón
                pdf.add_parrafo(linea[1:].strip() if linea.startswith('-') else linea, es_bullet=linea.startswith('-'))
            pdf.guardar()
            st.success("¡PDF generado!")
            st.download_button("⬇️ Descargar PDF", buf.getvalue(), f"{tema_n}.pdf")
