from hashlib import sha256
from io import BytesIO
import math

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import code128
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

PI_DIGITS = (
    "3141592653589793238462643383279502884197169399375105820974944592"
    "3078164062862089986280348253421170679821480865132823066470938446"
    "0955058223172535940812848111745028410270193852110555964462294895"
    "4930381964428810975665933446128475648233786783165271201909145648"
    "5669234603486104543266482133936072602491412737245870066063155881"
    "7488152092096282925409171536436789259036001133053054882046652138"
    "4146951941511609433057270365759591953092186117381932611793105118"
    "5480744623799627495673518857527248912279381830119491298336733624"
    "4065664308602139494639522473719070217986094370277053921717629317"
    "6752384674818467669405132000568127145263560827785771342757789609"
    "1736371787214684409012249534301465495853710507922796892589235415"
    "1160935413144014822445511009538837863609506800642251252051173929"
)


def _pi_slice(offset: int, length: int) -> str:
    doubled = PI_DIGITS * ((length // len(PI_DIGITS)) + 2)
    start = offset % len(PI_DIGITS)
    return doubled[start : start + length]


def generate_certificate_pdf(certificate):
    buffer = BytesIO()
    width, height = A4
    pdf = canvas.Canvas(buffer, pagesize=A4)

    bg = _pi_slice(certificate.pk * 13, 800)
    pdf.setFont("Courier", 6)
    pdf.setFillColor(colors.HexColor("#cfd4df"))
    y = height - 20
    while y > 20:
        pdf.drawString(20, y, bg[:80])
        y -= 10

    margin = 20 * mm
    pdf.setLineWidth(4)
    pdf.setStrokeColor(colors.HexColor("#f2c14e"))
    pdf.rect(margin, margin, width - margin * 2, height - margin * 2)
    pdf.setLineWidth(2)
    for layer in range(3):
        offset = layer * 12
        pdf.setStrokeColor(colors.HexColor("#d4af37" if layer % 2 == 0 else "#914e2c"))
        pdf.setDash(3, 2)
        pdf.rect(margin + offset, margin + offset, width - margin * 2 - offset * 2, height - margin * 2 - offset * 2)
    pdf.setDash()
    pdf.setStrokeColor(colors.HexColor("#f6e7c1"))
    for arc in range(6):
        pdf.setLineWidth(1.5)
        radius = (width / 2 - margin) - arc * 20
        pdf.arc(width / 2 - radius, height / 2 - radius, width / 2 + radius, height / 2 + radius, startAng=0, extent=180)
        pdf.arc(width / 2 - radius, height / 2 - radius, width / 2 + radius, height / 2 + radius, startAng=180, extent=180)
    pdf.setStrokeColor(colors.HexColor("#f4c5c5"))
    for petal in range(12):
        angle = petal * 30
        pdf.setLineWidth(1)
        rad = math.radians(angle)
        pdf.line(
            width / 2 + (width / 4) * math.cos(rad),
            height / 2 + (height / 4) * math.sin(rad),
            width / 2 + (width / 2 - margin) * math.cos(rad),
            height / 2 + (height / 2 - margin) * math.sin(rad),
        )

    pdf.setFont("Times-Bold", 32)
    pdf.setFillColor(colors.HexColor("#0a0a0a"))
    pdf.drawCentredString(width / 2, height - margin - 40, "CERTIFICADO")
    pdf.setFont("Times-Bold", 16)
    pdf.setFillColor(colors.HexColor("#173f7e"))
    pdf.drawCentredString(width / 2, height - margin - 64, "OFICIAL")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(margin + 10, height - margin - 80, f"Aluno: {certificate.student.name}")
    pdf.drawString(margin + 10, height - margin - 100, f"Curso: {certificate.course.title}")
    pdf.drawString(margin + 10, height - margin - 120, f"Emitido em: {certificate.issued_at.strftime('%d/%m/%Y %H:%M') if certificate.issued_at else '—'}")
    pdf.drawString(margin + 10, height - margin - 140, f"Código: {certificate.code or certificate.pk}")

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(margin + 10, height - margin - 180, "Notas de exames")
    pdf.setFont("Helvetica", 11)
    table_y = height - margin - 200
    pdf.drawString(margin + 10, table_y, "Disciplina")
    pdf.drawString(margin + 200, table_y, "Tipo")
    pdf.drawString(margin + 320, table_y, "Nota")
    table_y -= 20
    for record in certificate.records.all()[:10]:
        pdf.drawString(margin + 10, table_y, record.subject.name)
        pdf.drawString(margin + 200, table_y, record.exam_type.capitalize())
        pdf.drawString(margin + 320, table_y, f"{record.score}")
        table_y -= 18
        if table_y < margin + 50:
            break

    security_code = sha256(f"{certificate.tenant_id}-{certificate.pk}".encode()).hexdigest()[:16]
    pdf.setFillColor(colors.HexColor("#4b4b4b"))
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(margin + 10, margin + 30, f"Documento seguro – código de verificação: {security_code}")
    pdf.drawString(margin + 10, margin + 15, "Documento emitido digitalmente; qualquer tentativa de edição invalida o registro.")

    barcode_value = f"{certificate.tenant_id}-{certificate.code or certificate.pk}"
    barcode = code128.Code128(barcode_value, barHeight=30, barWidth=1.2)
    barcode.drawOn(pdf, margin, margin + 50)

    qr_value = f"https://schoolar.example.com/certificates/{certificate.pk}"
    qr = QrCodeWidget(qr_value)
    size = 70
    qr_drawing = Drawing(size, size)
    qr_drawing.add(qr)
    renderPDF.draw(qr_drawing, pdf, width - margin - size, height - margin - size - 10)

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
