import streamlit as st
import os, io, docx, PyPDF2
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from odf import text, teletype
from odf.opendocument import load

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="OTE Studio PRO", layout="centered")

# Colores OTE
C = {
    'lila_tema': HexColor("#E8E2E8"),
    'mint_osc': HexColor("#48B5A0"),
    'rosa_soft': HexColor("#FFD3B6"),
    'texto': HexColor("#3D3D3D"),
    'gris_puntos': HexColor("#D1D1D1")
}

# --- MOTOR GRÁFICO ---
class OTEGenerator:
    def __init__(self, buffer, tema):
        self.buffer = buffer
        self.tema = tema
        self.PAGE_W, self.PAGE_H = 1024, 704
        self.y = self.PAGE_H - 130
        self.c = canvas.Canvas(self.buffer, pagesize=(self.PAGE_W, self.PAGE_H))
        self.cargar_recursos()
        self.dibujar_plantilla()

    def cargar_recursos(self):
        f_path = os.path.join("assets", "fonts", "PatrickHand.ttf")
        if os.path.exists(f_path):
            pdfmetrics.registerFont(TTFont('PatrickHand', f_path))
        else: st.warning("⚠️ No se encontró la fuente PatrickHand")

    def dibujar_plantilla(self):
        # 1. Fondo de puntos
        self.c.setFillColor(white); self.c.rect(0,0,self.PAGE_W,self.PAGE_H,fill=1)
        self.c.setFillColor(C['gris_puntos'])
        for x in range(30, 1010, 30):
            for y in range(30, 680, 30):
                self.c.circle(x, y, 0.6, fill=1, stroke=0)
        
        # 2. Caja lila del tema
        self.c.setFillColor(C['lila_tema'])
        self.c.roundRect(362, self.PAGE_H-65, 300, 32, 6, fill=1)
        self.c.setFont('PatrickHand' if 'PatrickHand' in pdfmetrics.getRegisteredFontNames() else 'Helvetica', 17)
        self.c.setFillColor(C['texto'])
        self.c.drawCentredString(512, self.PAGE_H-58, self.tema.upper())
        self.c.drawRightString(self.PAGE_W-50, self.PAGE_H-58, "OPOSITA EN TIEMPO EXPRESS")

    def check_salto(self, pixeles):
        if self.y < pixeles:
            self.c.showPage()
            self.dibujar_plantilla()
            self.y = self.PAGE_H - 130

    def add_linea(self, txt):
        self.check_salto(40)
        self.c.setFont('PatrickHand' if 'PatrickHand' in pdfmetrics.getRegisteredFontNames() else 'Helvetica', 14)
        self.c.drawString(70, self.y, txt)
        self.y -= 25

    def add_bullet(self, txt):
        self.check_salto(40)
        self.c.setFillColor(HexColor("#E8B4B8"))
        self.c.circle(75, self.y+5, 4, fill=1) # Corazón
        self.c.setFillColor(C['texto'])
        self.c.drawString(90, self.y, txt)
        self.y -= 25

    def finalizar(self):
        self.c.save()

# --- LECTORES ---
def extraer_texto(f):
    if f.name.endswith('.docx'): return "\n".join([p.text for p in docx.Document(f).paragraphs])
    if f.name.endswith('.pdf'): return "\n".join([p.extract_text() for p in PyPDF2.PdfReader(f).pages])
    return ""

# --- INTERFAZ ---
# (Aquí va la lógica de password que ya tienes configurada en los Secrets)
st.title("📝 OTE Studio PRO")
tema_input = st.text_input("Nombre del Tema", "Tema 1")
metodo = st.radio("Entrada:", ["Subir Archivo", "Pegar Texto"])

input_final = ""
if metodo == "Subir Archivo":
    file = st.file_uploader("Documento", type=['docx', 'pdf'])
    if file: input_final = extraer_texto(file)
else:
    input_final = st.text_area("Pega tus apuntes:", height=300)

if st.button("✨ Generar PDF Bonito"):
    if input_final:
        buf = io.BytesIO()
        pdf = OTEGenerator(buf, tema_input)
        for l in input_final.split('\n'):
            if l.startswith('-'): pdf.add_bullet(l[1:].strip())
            else: pdf.add_linea(l.strip())
        pdf.finalizar()
        st.download_button("⬇️ Descargar PDF", buf.getvalue(), f"{tema_input}.pdf")
