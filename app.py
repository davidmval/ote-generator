import streamlit as st
import os, io, docx, PyPDF2
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="OTE Studio Cloud", layout="centered")

# --- FUNCIONES DE SEGURIDAD ---
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

# --- MOTOR DE DIBUJO ---
class OTEGenerator:
    def __init__(self, buffer, tema):
        self.buffer = buffer
        self.tema = tema
        self.PAGE_W, self.PAGE_H = 1024, 704
        self.y = self.PAGE_H - 130
        self.c = canvas.Canvas(self.buffer, pagesize=(self.PAGE_W, self.PAGE_H))
        self.registrar_fuentes()
        self.dibujar_fondo()

    def registrar_fuentes(self):
        ruta_fuente = os.path.join("assets", "fonts", "PatrickHand.ttf")
        if os.path.exists(ruta_fuente):
            pdfmetrics.registerFont(TTFont('PatrickHand', ruta_fuente))
        else:
            # Si no hay fuente, usamos Helvetica por defecto para no colgar la app
            pass 

    def dibujar_fondo(self):
        # Banner lila y puntos
        self.c.setFillColor(white); self.c.rect(0,0,self.PAGE_W,self.PAGE_H,fill=1)
        self.c.setFillColor(HexColor("#D1D1D1"))
        for x in range(30, 1010, 30):
            for y in range(30, 680, 30):
                self.c.circle(x, y, 0.6, fill=1, stroke=0)
        self.c.setFillColor(HexColor("#E8E2E8"))
        self.c.roundRect(362, self.PAGE_H-65, 300, 32, 6, fill=1)
        self.c.setFont('PatrickHand' if 'PatrickHand' in pdfmetrics.getRegisteredFontNames() else 'Helvetica', 17)
        self.c.setFillColor(HexColor("#3D3D3D"))
        self.c.drawCentredString(512, self.PAGE_H-58, self.tema.upper())

    def agregar_texto(self, txt):
        if self.y < 50: # Salto de página
            self.c.showPage()
            self.dibujar_fondo()
            self.y = self.PAGE_H - 130
        self.c.drawString(70, self.y, txt[:100]) # Evitar textos infinitos
        self.y -= 25

    def guardar(self):
        self.c.save()

# --- APP PRINCIPAL ---
if check_password():
    st.title("📝 OTE Studio: Generador")
    tema = st.text_input("Nombre del Tema:", "Tema 1")
    texto = st.text_area("Pega tus apuntes aquí:", height=300)
    
    if st.button("✨ Generar PDF"):
        if texto:
            try:
                buf = io.BytesIO()
                pdf = OTEGenerator(buf, tema)
                for linea in texto.split('\n'):
                    if linea.strip(): pdf.agregar_texto(linea.strip())
                pdf.guardar()
                st.success("¡PDF generado con éxito!")
                st.download_button("⬇️ Descargar PDF", buf.getvalue(), f"{tema}.pdf", "application/pdf")
            except Exception as e:
                st.error(f"Error al generar el PDF: {e}")
        else:
            st.warning("Escribe algo de texto primero.")
