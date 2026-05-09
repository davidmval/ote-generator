import streamlit as st
import os, io, docx, PyPDF2
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

# --- COLORES OTE ---
C = {
    'lila_caja': HexColor("#E8E2E8"),
    'gris_puntos': HexColor("#D1D1D1"),
    'texto': HexColor("#3D3D3D"),
    'rosa_corazon': HexColor("#E8B4B8")
}

# --- SEGURIDAD ---
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
            else: st.error("Contraseña incorrecta")
        return False
    return True

# --- MOTOR DE DIBUJO ---
class OTEGenerator:
    def __init__(self, buffer, tema):
        self.buffer = buffer
        self.tema = tema
        self.PAGE_W, self.PAGE_H = 1024, 704
        self.y = self.PAGE_H - 140
        self.c = canvas.Canvas(self.buffer, pagesize=(self.PAGE_W, self.PAGE_H))
        self.font_name = self.cargar_recursos()
        self.dibujar_plantilla()

    def buscar_archivo(self, nombre, carpetas):
        """Busca un archivo en varias rutas posibles."""
        for carpeta in carpetas:
            ruta = os.path.join(carpeta, nombre)
            if os.path.exists(ruta):
                return ruta
        return None

    def cargar_recursos(self):
        # Rutas donde buscar las fuentes
        rutas_busqueda = ["assets", "assets/fonts", "."]
        f_path = self.buscar_archivo("PatrickHand.ttf", rutas_busqueda)
        
        if f_path:
            try:
                pdfmetrics.registerFont(TTFont('PatrickHand', f_path))
                return 'PatrickHand'
            except: pass
        return 'Helvetica'

    def dibujar_plantilla(self):
        # 1. Fondo de puntos
        self.c.setFillColor(white); self.c.rect(0,0,self.PAGE_W,self.PAGE_H,fill=1,stroke=0)
        self.c.setFillColor(C['gris_puntos'])
        for x in range(30, 1010, 35):
            for y in range(30, 680, 35):
                self.c.circle(x, y, 0.7, fill=1, stroke=0)
        
        # 2. Caja lila central para el tema
        self.c.setFillColor(C['lila_caja'])
        self.c.roundRect(362, self.PAGE_H-65, 300, 32, 6, fill=1, stroke=0)
        self.c.setFont(self.font_name, 17); self.c.setFillColor(C['texto'])
        self.c.drawCentredString(512, self.PAGE_H-58, self.tema.upper())
        
        # 3. Marca de agua y Logo
        self.c.drawRightString(self.PAGE_W-50, self.PAGE_H-58, "OPOSITA EN TIEMPO EXPRESS")
        
        rutas_img = ["assets", "assets/img", "."]
        logo_path = self.buscar_archivo("template_img_1.png", rutas_img)
        if logo_path:
            self.c.drawImage(logo_path, 930, self.PAGE_H-110, 60, 52, mask='auto')

    def add_texto(self, texto, bullet=False):
        # Ajuste de línea automático para que no se corte
        x_pos = 95 if bullet else 70
        ancho = 820 if bullet else 880
        lineas = simpleSplit(texto, self.font_name, 15, ancho)
        
        if self.y - (len(lineas) * 25) < 60:
            self.c.showPage()
            self.dibujar_plantilla()
            self.y = self.PAGE_H - 140

        if bullet:
            self.c.setFillColor(C['rosa_corazon']) # Corazón rosa
            self.c.circle(80, self.y + 5, 4, fill=1, stroke=0)
            self.c.setFillColor(C['texto'])

        self.c.setFont(self.font_name, 15)
        for linea in lineas:
            self.c.drawString(x_pos, self.y, linea)
            self.y -= 25

    def finalizar(self):
        self.c.save()

# --- INTERFAZ ---
if check_password():
    st.title("📝 OTE Studio PRO")
    
    with st.sidebar:
        tema_n = st.text_input("Nombre del Tema", "Tema 1")
        metodo = st.radio("Entrada:", ["Subir Archivo", "Pegar Texto"])

    input_final = ""
    if metodo == "Subir Archivo":
        f = st.file_uploader("Sube tu Word o PDF", type=['docx', 'pdf'])
        if f:
            if f.name.endswith('.docx'):
                input_final = "\n".join([p.text for p in docx.Document(f).paragraphs])
            else:
                input_final = "\n".join([page.extract_text() for page in PyPDF2.PdfReader(f).pages])
    else:
        input_final = st.text_area("Pega tus apuntes:", height=300)

    if st.button("✨ Generar PDF Bonito"):
        if input_final:
            buf = io.BytesIO()
            pdf = OTEGenerator(buf, tema_n)
            for l in input_final.split('\n'):
                linea = l.strip()
                if linea:
                    # Si la línea empieza con guion, pone el corazón rosa
                    pdf.add_texto(linea[1:].strip() if linea.startswith('-') else linea, bullet=linea.startswith('-'))
            pdf.finalizar()
            st.success("¡PDF generado!")
            st.download_button("⬇️ Descargar PDF", buf.getvalue(), f"{tema_n}.pdf")
