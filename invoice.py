from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

styles = getSampleStyleSheet()
styleN = styles["Normal"]
styleH = styles["Heading1"]

def generate_invoice(bill_id, items, total, datetime_str, gst=0, save_path="invoices", subtotal=None):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    if subtotal is None:
        subtotal = total - gst

    filename = os.path.join(save_path, f"invoice_{bill_id}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    # Header
    elements.append(Paragraph("<b>AMBICA SELECTION</b>", styles["Title"]))
    elements.append(Paragraph("DURGA MATA CHOWCK NAMPUR", styles["Normal"]))
    elements.append(Paragraph(f"Contact: 9175573469", styles["Normal"]))
    elements.append(Paragraph(f"Bill No: {bill_id}", styles["Normal"]))
    elements.append(Paragraph(f"Date: {datetime_str}", styles["Normal"]))
    elements.append(Paragraph(f"GSTIN/UNI: 27ADSPW7699E1ZE", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Table data
    data = [["Item", "Price", "Qty", "Total"]]
    for item in items:
        data.append([
            item["name"],
            f"{item['price']:.2f}",
            str(item["quantity"]),
            f"{item['price'] * item['quantity']:.2f}"
        ])

    # Add totals inside table
    data.append(["", "", "Subtotal", f"{subtotal:.2f}"])
    data.append(["", "", "GST (5%)", f"{gst:.2f}"])
    data.append(["", "", "Grand Total", f"{total:.2f}"])

    table = Table(data, colWidths=[200, 100, 80, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # header row
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),

        # Make totals bold
        ('FONTNAME', (-2, -3), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (-2, -1), (-1, -1), colors.lightgrey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Name: ____________________________", styleN))
    elements.append(Paragraph("Phone Number: ____________________", styleN))
    elements.append(Paragraph("Payment (Cash / UPI / Card): ____________________", styleN))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<b>Thank you for shopping with us!</b>", styles["Heading3"]))

    doc.build(elements)
    return filename
