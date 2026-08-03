# core/gerador_pdf.py
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, logo_path="", rodape_texto="", **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.logo_path = logo_path
        self.rodape_texto = rodape_texto

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        top_y = 828

        display_h = 0
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                img = ImageReader(self.logo_path)
                iw, ih = img.getSize()
                aspect = ih / float(iw)
                display_w = 110
                display_h = display_w * aspect
                if display_h > 30:
                    display_h = 30
                    display_w = display_h / aspect
                self.drawImage(img, 36, top_y - display_h, width=display_w, height=display_h, mask='auto')
            except Exception:
                self.setFont("Helvetica-Bold", 10)
                self.setFillColor(colors.HexColor("#0F2C59"))
                self.drawString(36, top_y - 10, "PARECER TÉCNICO REVISIONAL")
        else:
            self.setFont("Helvetica-Bold", 10)
            self.setFillColor(colors.HexColor("#0F2C59"))
            self.drawString(36, top_y - 10, "PARECER TÉCNICO REVISIONAL - MEMÓRIA DE CÁLCULO")

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#555555"))
        self.drawRightString(559, top_y - 10, "Documento Auditável para Instrução Processual")

        line_y = top_y - (display_h if display_h > 0 else 15) - 4
        self.setStrokeColor(colors.HexColor("#0F2C59"))
        self.setLineWidth(1)
        self.line(36, line_y, 559, line_y)

        # Rodapé
        self.setStrokeColor(colors.HexColor("#D3D3D3"))
        self.setLineWidth(0.5)
        self.line(36, 48, 559, 48)

        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#444444"))
        texto_rodape = self.rodape_texto if self.rodape_texto.strip() else "Sistema Pericial Revisional (PRICE/SAC)"
        self.drawString(36, 34, texto_rodape[:90])

        self.drawRightString(559, 34, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()


def exportar_pdf(filepath, params, resumo, memoria, logo_path="", rodape_texto=""):
    doc = SimpleDocTemplate(filepath, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=85, bottomMargin=54)
    styles = getSampleStyleSheet()
    normal = styles['Normal']

    title_style = ParagraphStyle('DocTitle', parent=normal, fontName='Helvetica-Bold', fontSize=14, leading=18,
                                 textColor=colors.HexColor('#0F2C59'), alignment=1)
    h2_style = ParagraphStyle('DocH2', parent=normal, fontName='Helvetica-Bold', fontSize=11, leading=14,
                              textColor=colors.HexColor('#0F2C59'), spaceBefore=12, spaceAfter=6)

    elements = [
        Paragraph("DEMONSTRATIVO TÉCNICO PERICIAL DE REVISÃO CONTRATUAL", title_style),
        Spacer(1, 15),
        Paragraph("1. PARÂMETROS DO RECALCULO", h2_style)
    ]

    param_data = [
        ["Valor Financiado Bruto:", f"R$ {params['val_bruto']:,.2f}", "Sistema Amortização:", params['sistema']],
        ["(-) Tarifas/Seguros Expurgo:", f"R$ {params['tarifas']:,.2f}", "Taxa Juros Contrato:",
         f"{params['taxa_banco'] * 100:.2f}% a.m."],
        ["Prazo Financiamento:", f"{params['prazo']} parcelas", "Taxa Juros Ref. BACEN:",
         f"{params['taxa_bacen'] * 100:.2f}% a.m."]
    ]
    t_param = Table(param_data, colWidths=[130, 130, 130, 133])
    t_param.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D3D3D3')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.extend([t_param, Spacer(1, 15), Paragraph("2. APURAÇÃO DO INDÉBITO (RESTITUIÇÃO)", h2_style)])

    card_data = [
        ["Total Pago Real", "Total Recalculado", "Restituição Simples", "Restituição em Dobro (Art. 42 CDC)"],
        [f"R$ {resumo['tot_pago']:,.2f}", f"R$ {resumo['tot_devido']:,.2f}", f"R$ {resumo['tot_dif']:,.2f}",
         f"R$ {resumo['tot_dobro']:,.2f}"]
    ]
    t_cards = Table(card_data, colWidths=[130, 130, 130, 133])
    t_cards.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F2C59')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D3D3D3')),
        ('TEXTCOLOR', (2, 1), (2, 1), colors.HexColor('#2980B9')),
        ('TEXTCOLOR', (3, 1), (3, 1), colors.HexColor('#8E44AD')),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
    ]))
    elements.extend([t_cards, Spacer(1, 15), Paragraph("3. MEMÓRIA DE CÁLCULO DETALHADA", h2_style)])

    tbl_data = [
        ["Nº", "Pago Real", "Saldo Inic.", "Juros", "Amortização", "Prest. Correta", "Saldo Final", "Diferença"]]
    for item in memoria:
        tbl_data.append([
            str(item['parcela']),
            f"R$ {item['pago_real']:,.2f}",
            f"R$ {item['saldo_inicial']:,.2f}",
            f"R$ {item['juros']:,.2f}",
            f"R$ {item['amortizacao']:,.2f}",
            f"R$ {item['prestacao_correta']:,.2f}",
            f"R$ {item['saldo_final']:,.2f}",
            f"R$ {item['diferenca']:,.2f}"
        ])

    t_mem = Table(tbl_data, colWidths=[25, 70, 75, 65, 70, 75, 75, 68])
    t_mem.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3E62')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#D3D3D3')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFD')]),
    ]))
    elements.append(t_mem)

    def make_canvas(*args, **kwargs):
        return NumberedCanvas(*args, logo_path=logo_path, rodape_texto=rodape_texto, **kwargs)

    doc.build(elements, canvasmaker=make_canvas)

gerar_pdf_revisional = exportar_pdf