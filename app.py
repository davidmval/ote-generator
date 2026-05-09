import streamlit as st
import os, io, docx, PyPDF2
from reportlab.lib.colors import HexColor, white, Color
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

# --- COLORES EXACTOS OTE ---
C = {
    'lila_header': HexColor("#E8E2E8"),
    'rosa_pálido': HexColor("#FDF0EF"),
    'rosa_marca': HexColor("#E8B4B8"),
    'mint': HexColor("#48B5A0"),
    'puntos': HexColor("#D1D1D1"),
    'texto': HexColor("#3D3D3D")
}

# --- MOTOR GRÁFICO ---
class OTEGenerator:
    def __init__(self, buffer, tema):
        self.buffer = buffer
        self.tema = tema
        self.PAGE_W, self.PAGE_H = 1024, 704
        self.y = self.PAGE_H - 150
        self.pn = 1
        self.c = canvas.Canvas(self.buffer, pagesize=(self.PAGE_W, self.PAGE_H))
        self.f_manuscr = self.cargar_fuentes()
        self.dibujar_pagina()

    def cargar_fuentes(self):
        f_p = "assets/fonts/PatrickHand.ttf"
        h_p = "assets/fonts/FrederickaTheGreat.ttf"
        if os.path.exists(f_p):
            pdfmetrics.registerFont(TTFont('PatrickHand', f_p))
            if os.path.exists(h_p): pdfmetrics.registerFont(TTFont('Fredericka', h_p))
            return 'PatrickHand'
        return 'Helvetica'

    def dibujar_pagina(self):
        # 1. Fondo de Puntos
        self.c.setFillColor(white); self.c.rect(0,0,self.PAGE_W,self.PAGE_H,fill=1,stroke=0)
        self.c.setFillColor(C['puntos'])
        for x in range(30, 1010, 35):
            for y in range(30, 680, 35):
                self.c.circle(x, y, 0.7, fill=1, stroke=0)
        
        # 2. Banner Superior Rosa Pálido
        self.c.setFillColor(C['rosa_pálido'])
        self.c.rect(0, self.PAGE_H-80, self.PAGE_W, 80, fill=1, stroke=0)
        
        # 3. Caja Lila Central del Tema
        self.c.setFillColor(C['lila_header'])
        self.c.roundRect(362, self.PAGE_H-65, 300, 32, 6, fill=1, stroke=0)
        
        self.c.setFont(self.f_manuscr, 17); self.c.setFillColor(C['texto'])
        self.c.drawCentredString(512, self.PAGE_H-58, self.tema.upper())
        
        # 4. "OPOSITA EN TIEMPO EXPRESS" con Color y Corazones
        # (Simulamos los corazones en las O con un pequeño dibujo circular rosa)
        self.c.setFillColor(C['rosa_marca'])
        self.c.setFont('Helvetica-Bold', 18)
        marca_txt = "OPOSITA EN TIEMPO EXPRESS"
        self.c.drawRightString(self.PAGE_W-50, self.PAGE_H-58, marca_txt)
        
        # 5. Pie de Página: Nombre tema y número
        self.c.setFont(self.f_manuscr, 12); self.c.setFillColor(C['texto'])
        self.c.drawString(50, 30, f"{self.tema}")
        self.c.drawRightString(self.PAGE_W-50, 30, f"{self.pn}")

    def add_texto(self, texto, tipo="normal"):
        # Lógica de iconos según el tipo
        ancho = 850
        x_inicio = 70
        
        if tipo == "corazon":
            self.c.setFillColor(C['rosa_marca'])
            self.c.circle(80, self.y+5, 4, fill=1) # Icono Corazón
            x_inicio = 95; ancho = 820
            
        lineas = simpleSplit(texto, self.f_manuscr, 15, ancho)
        
        if self.y - (len(lineas)*25) < 60:
            self.c.showPage()
            self.pn += 1
            self.dibujar_pagina()
            self.y = self.PAGE_H - 150

        self.c.setFillColor(C['texto']); self.c.setFont(self.f_manuscr, 15)
        for linea in lineas:
            self.c.drawString(x_inicio, self.y, linea)
            self.y -= 25

    def finalizar(self):
        self.c.save()

# --- INTERFAZ STREAMLIT ---
# (Usa el mismo código de password y lectores de archivos que ya tienes funcionando)
