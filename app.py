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

if check_password():
    class OTEGenerator:
        def __init__(self, buffer, tema):
            self.buffer = buffer
            self.tema = tema
            self.PAGE_W, self.PAGE_H = 1024, 704
            self.y = self.PAGE_H - 140
            self.c = canvas.Canvas(self.buffer, pagesize=(self.PAGE_W, self.PAGE_H))
            self.cargar_recursos()
            self.dibujar_plantilla()

        def cargar_recursos(self):
            # Nombres exactos de tu pantallazo
            fuentes = [
                ('PatrickHand', 'assets/fonts/PatrickHand.ttf'),
                ('Fredericka', 'assets/fonts/FrederickaTheGreat.ttf')
            ]
            for name, path in fuentes:
                if os.path.exists(path):
                    pdfmetrics.registerFont(TTFont(name, path))

        def dibujar_plantilla(self):
            # Fondo de puntos
            self.c.setFillColor(white); self.c.rect(0,0,self.PAGE_W,self.PAGE_H,fill=1)
            self.c.setFillColor(HexColor("#D1D1D1"))
            for x in range(30, 1010, 35):
                for y in range(30, 680, 35):
                    self.c.circle(x, y, 0.7, fill=1, stroke=0)
            
            # Caja tema central
            self.c.setFillColor(HexColor("#E8E2E8"))
            self.c.roundRect(362, self.PAGE_H-65, 300, 32, 6, fill=1)
            
            font = 'PatrickHand' if 'PatrickHand' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
            self.c.setFont(font, 18); self.c.setFillColor(HexColor("#3D3D3D"))
            self.c.drawCentredString(512, self.PAGE_H-58, self.tema.upper())
            
            # Logo (template_img_1.png de tu carpeta img)
            logo_path = 'assets/img/template_img_1.png'
            if os.path.exists(logo_path):
                self.c.drawImage(logo_path, 930, self.PAGE_H-110, 60, 52, mask='auto')

        def escribir_texto(self, texto, bullet=False):
            # Ajuste de línea automático (Wrapping)
            x_pos = 95 if bullet else 70
            ancho = 820 if bullet else 850
            font = 'PatrickHand' if 'PatrickHand' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
            
            lineas = simpleSplit(texto, font, 15, ancho)
            
            if self.y - (len(lineas) * 25) < 60:
                self.c.showPage()
                self.dibujar_plantilla()
                self.y = self.PAGE_H - 140

            if bullet:
                self.c.setFillColor(HexColor("#E8B4B8")) # Corazón rosa
                self.c.circle(80, self.y + 5, 4, fill=1)
                self.c.setFillColor(HexColor("#3D3D3D"))

            self.c.setFont(font, 15)
            for linea in lineas:
                self.c.drawString(x_pos, self.y, linea)
                self.y -= 25

        def finalizar(self):
            self.c.save()

    # --- INTERFAZ ---
    st.title("📝 OTE Studio PRO")
    tema_n = st.text_input("Nombre del Tema:", "Tema 1 IASS")
    entrada = st.text_area("Contenido (usa '-' para corazones):", height=300)

    if st.button("✨ Generar PDF OTE"):
        if entrada:
            buf = io.BytesIO()
            pdf = OTEGenerator(buf, tema_n)
            for parrafo in entrada.split('\n'):
                if parrafo.strip():
                    if parrafo.strip().startswith('-'):
                        pdf.escribir_texto(parrafo.strip()[1:].strip(), bullet=True)
                    else:
                        pdf.escribir_texto(parrafo.strip())
            pdf.finalizar()
            st.success("¡PDF generado!")
            st.download_button("⬇️ Descargar PDF", buf.getvalue(), f"{tema_n}.pdf")
