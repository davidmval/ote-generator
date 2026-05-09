import streamlit as st
import os, io, docx, PyPDF2
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

# --- COLORES OFICIALES OTE ---
C = {
    'rosa_pálido': HexColor("#FDF0EF"),
    'lila_tema': HexColor("#E8E2E8"),
    'marca_agua': HexColor("#E8B4B8"),
    'gris_puntos': HexColor("#D1D1D1"),
    'texto': HexColor("#3D3D3D"),
    'mint': HexColor("#48B5A0")
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

# --- MOTOR DE GENERACIÓN PDF ---
class OTEGenerator:
    def __init__(self, buffer, tema):
        self.buffer = buffer
        self.tema = tema
        self.PAGE_W, self.PAGE_H = 1024, 704
        self.y = self.PAGE_H - 150
        self.pn = 1
        self.c = canvas.Canvas(self.buffer, pagesize=(self.PAGE_W, self.PAGE_H))
        self.font_main = self.cargar_recursos()
        self.dibujar_pagina()

    def cargar_recursos(self):
        base = os.path.dirname(__file__)
        f1 = os.path.join(base, "assets", "PatrickHand.ttf")
        f2 = os.path.join(base, "assets", "FrederickaTheGreat.ttf")
        try:
            if os.path.exists(f1):
                pdfmetrics.registerFont(TTFont('PatrickHand', f1))
                if os.path.exists(f2):
                    pdfmetrics.registerFont(TTFont('Fredericka', f2))
                return 'PatrickHand'
        except: pass
        return 'Helvetica'

    def dibujar_pagina(self):
        # 1. Fondo de puntos (Iconografía)
        self.c.setFillColor(white); self.c.rect(0,0,self.PAGE_W,self.PAGE_H,fill=1,stroke=0)
        self.c.setFillColor(C['gris_puntos'])
        for x in range(30, 1010, 35):
            for y in range(30, 680, 35):
                self.c.circle(x, y, 0.7, fill=1, stroke=0)
        
        # 2. Banner Superior Rosa Pálido (Plantilla)
        self.c.setFillColor(C['rosa_pálido'])
        self.c.rect(0, self.PAGE_H-80, self.PAGE_W, 80, fill=1, stroke=0)
        
        # 3. Caja Lila Central del Tema
        self.c.setFillColor(C['lila_tema'])
        self.c.roundRect(362, self.PAGE_H-65, 300, 32, 6, fill=1, stroke=0)
        
        # 4. Texto del Tema
        self.c.setFont(self.font_main, 17); self.c.setFillColor(C['texto'])
        self.c.drawCentredString(512, self.PAGE_H-58, self.tema.upper())
        
        # 5. Marca de Marca (DERECHA)
        self.c.setFillColor(C['marca_agua'])
        self.c.setFont('Helvetica-Bold', 16)
        self.c.drawRightString(self.PAGE_W-50, self.PAGE_H-58, "OPOSITA EN TIEMPO EXPRESS")
        
        # 6. Pie de Página (Footer)
        self.c.setFont(self.font_main, 12); self.c.setFillColor(C['texto'])
        self.c.drawString(50, 30, f"{self.tema}")
        self.c.drawRightString(self.PAGE_W-50, 30, f"Página {self.pn}")

    def add_parrafo(self, texto):
        es_bullet = texto.strip().startswith('-')
        es_titulo = texto.strip().startswith('#')
        
        clean_text = texto.strip()[1:].strip() if (es_bullet or es_titulo) else texto.strip()
        
        # Estilos según el trigger
        fuente = 'Fredericka' if es_titulo and 'Fredericka' in pdfmetrics.getRegisteredFontNames() else self.font_main
        size = 22 if es_titulo else 15
        color = C['mint'] if es_titulo else C['texto']
        x_start = 95 if es_bullet else 70
        ancho = 820 if es_bullet else 880

        lineas = simpleSplit(clean_text, fuente, size, ancho)
        
        if self.y - (len(lineas) * 25) < 80:
            self.c.showPage()
            self.pn += 1
            self.dibujar_pagina()
            self.y = self.PAGE_H - 150

        if es_bullet:
            self.c.setFillColor(C['marca_agua'])
            self.c.circle(80, self.y + 5, 4, fill=1, stroke=0) # Corazón rosa

        self.c.setFillColor(color); self.c.setFont(fuente, size)
        for linea in lineas:
            self.c.drawString(x_start, self.y, linea)
            self.y -= 25
        self.y -= 5

    def guardar(self):
        self.c.save()

# --- INTERFAZ STREAMLIT ---
if check_password():
    st.title("📝 OTE Studio PRO: Generador de Apuntes")
    
    with st.sidebar:
        tema_n = st.text_input("Nombre del Tema", "Tema 1 IASS")
        metodo = st.radio("Entrada:", ["Subir Documento", "Pegar Texto"])

    contenido = ""
    if metodo == "Subir Documento":
        f = st.file_uploader("Sube Word o PDF", type=['docx', 'pdf'])
        if f:
            if f.name.endswith('.docx'):
                contenido = "\n".join([p.text for p in docx.Document(f).paragraphs])
            else:
                reader = PyPDF2.PdfReader(f)
                contenido = "\n".join([p.extract_text() for p in reader.pages])
    else:
        contenido = st.text_area("Pega tus apuntes aquí:", height=350)

    if st.button("✨ Generar PDF con Estilo OTE"):
        if contenido:
            buf = io.BytesIO()
            gen = OTEGenerator(buf, tema_n)
            for bloque in contenido.split('\n'):
                if bloque.strip(): gen.add_parrafo(bloque)
            gen.guardar()
            st.success("¡PDF generado correctamente!")
            st.download_button("⬇️ Descargar PDF", buf.getvalue(), f"{tema_n}.pdf")
