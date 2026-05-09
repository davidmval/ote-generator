import streamlit as st
import os, io, docx, PyPDF2
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

# --- CONFIGURACIÓN DE COLORES OFICIALES OTE ---
C = {
    'lila_header': HexColor("#E8E2E8"), # Caja central del tema
    'puntos_fondo': HexColor("#D1D1D1"), # Gris suave de los puntos
    'texto_principal': HexColor("#3D3D3D"),
    'rosa_corazon': HexColor("#E8B4B8"), # Rosa de la iconografía
    'mint_titulos': HexColor("#48B5A0") # Menta de los títulos
}

# --- SEGURIDAD ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        st.title("🔒 Acceso Oposita en Tiempo Express")
        pwd = st.text_input("Introduce la contraseña del equipo:", type="password")
        if st.button("Entrar"):
            if pwd == st.secrets["password"]:
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Contraseña incorrecta")
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
        self.font_text = self.cargar_fuentes()
        self.dibujar_entorno()

    def cargar_fuentes(self):
        f_path = "assets/fonts/PatrickHand.ttf"
        h_path = "assets/fonts/FrederickaTheGreat.ttf"
        try:
            if os.path.exists(f_path):
                pdfmetrics.registerFont(TTFont('PatrickHand', f_path))
                if os.path.exists(h_path):
                    pdfmetrics.registerFont(TTFont('Fredericka', h_path))
                return 'PatrickHand'
        except: pass
        return 'Helvetica'

    def dibujar_entorno(self):
        # 1. Fondo de puntos (Iconografía pág 1)
        self.c.setFillColor(white); self.c.rect(0,0,self.PAGE_W,self.PAGE_H,fill=1,stroke=0)
        self.c.setFillColor(C['puntos_fondo'])
        for x in range(30, 1010, 35):
            for y in range(30, 680, 35):
                self.c.circle(x, y, 0.7, fill=1, stroke=0)
        
        # 2. Caja Lila Superior (Plantilla)
        self.c.setFillColor(C['lila_header'])
        self.c.roundRect(362, self.PAGE_H-65, 300, 32, 6, fill=1, stroke=0)
        
        # 3. Textos del Header
        font_header = 'PatrickHand' if 'PatrickHand' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        self.c.setFont(font_header, 17); self.c.setFillColor(C['texto_principal'])
        self.c.drawCentredString(512, self.PAGE_H-58, self.tema.upper())
        
        # Marca de marca y logo
        self.c.drawRightString(self.PAGE_W-50, self.PAGE_H-58, "OPOSITA EN TIEMPO EXPRESS")
        logo = "assets/img/template_img_1.png"
        if os.path.exists(logo):
            self.c.drawImage(logo, 930, self.PAGE_H-110, 60, 52, mask='auto')

    def add_bloque(self, texto):
        # Detectar tipo de contenido
        es_titulo = texto.startswith('#')
        es_bullet = texto.startswith('-')
        
        clean_text = texto[1:].strip() if (es_titulo or es_bullet) else texto
        
        # Configuración según tipo
        fuente = ('Fredericka' if es_titulo and 'Fredericka' in pdfmetrics.getRegisteredFontNames() else self.font_main if hasattr(self, 'font_main') else self.font_text)
        size = 24 if es_titulo else 15
        color = C['mint_titulos'] if es_titulo else C['texto_principal']
        x_start = 70 if not es_bullet else 95
        ancho = 880 if not es_bullet else 820

        # Ajuste de línea automático
        lineas = simpleSplit(clean_text, fuente, size, ancho)
        
        # Salto de página si no cabe
        if self.y - (len(lineas) * 25) < 60:
            self.c.showPage()
            self.dibujar_entorno()
            self.y = self.PAGE_H - 140

        if es_bullet:
            self.c.setFillColor(C['rosa_corazon']) # Corazón rosa
            self.c.circle(80, self.y + 5, 4, fill=1, stroke=0)

        self.c.setFont(fuente, size); self.c.setFillColor(color)
        for linea in lineas:
            self.c.drawString(x_start, self.y, linea)
            self.y -= 25
        self.y -= 5 # Espacio extra entre párrafos

    def guardar(self):
        self.c.save()

# --- LECTORES ---
def extraer_texto(f):
    if f.name.endswith('.docx'): return "\\n".join([p.text for p in docx.Document(f).paragraphs])
    if f.name.endswith('.pdf'): return "\\n".join([p.extract_text() for p in PyPDF2.PdfReader(f).pages])
    return ""

# --- INTERFAZ ---
if check_password():
    st.title("📝 OTE Studio PRO")
    with st.sidebar:
        tema_n = st.text_input("Nombre del Tema", "Tema 1 IASS")
        metodo = st.radio("Entrada:", ["Subir Documento", "Pegar Texto"])

    contenido = ""
    if metodo == "Subir Documento":
        archivo = st.file_uploader("Sube Word o PDF", type=['docx', 'pdf'])
        if archivo: contenido = extraer_texto(archivo)
    else:
        contenido = st.text_area("Pega tus apuntes:", height=300)

    if st.button("✨ Generar PDF OTE"):
        if contenido:
            buf = io.BytesIO()
            pdf = OTEGenerator(buf, tema_n)
            for parrafo in contenido.split('\\n'):
                if parrafo.strip():
                    pdf.add_bloque(parrafo.strip())
            pdf.guardar()
            st.success("¡PDF Generado con éxito!")
            st.download_button("⬇️ Descargar PDF", buf.getvalue(), f"{tema_n}.pdf")
