"""Génération de facture PDF."""
from io import BytesIO
from decimal import Decimal
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER

GREEN = HexColor('#2e7d32')
GRAY = HexColor('#64748b')
BORDER = HexColor('#e2e8f0')
LIGHT = HexColor('#f8fafc')


def _fmt(val):
    v = Decimal(str(val)).quantize(Decimal('0.01'))
    if v == v.to_integral_value():
        return f'${int(v)}'
    return f'${v}'


def generer_facture_pdf(facture):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch,
                            leftMargin=0.6*inch, rightMargin=0.6*inch)

    styles = getSampleStyleSheet()
    s = styles
    s.add(ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=22, textColor=GREEN, spaceAfter=2))
    s.add(ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=12, textColor=HexColor('#1a1a2e'), spaceAfter=4))
    s.add(ParagraphStyle('Body', fontName='Helvetica', fontSize=9, textColor=HexColor('#1a1a2e'), leading=13))
    s.add(ParagraphStyle('Small', fontName='Helvetica', fontSize=8, textColor=GRAY))
    s.add(ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=HexColor('#ffffff')))
    s.add(ParagraphStyle('TD', fontName='Helvetica', fontSize=9, textColor=HexColor('#1a1a2e'), leading=12))
    s.add(ParagraphStyle('TDB', fontName='Helvetica-Bold', fontSize=9, textColor=HexColor('#1a1a2e'), leading=12))
    s.add(ParagraphStyle('Right', fontName='Helvetica', fontSize=9, textColor=HexColor('#1a1a2e'), alignment=TA_RIGHT))
    s.add(ParagraphStyle('RightB', fontName='Helvetica-Bold', fontSize=10, textColor=GREEN, alignment=TA_RIGHT))

    el = []
    cmd = facture.commande
    client = cmd.client

    # Header
    el.append(Paragraph('FACTURE', s['H1']))
    el.append(Paragraph(facture.numero, s['H2']))
    el.append(Spacer(1, 10))

    # Info table
    info = [
        [Paragraph('<b>Herbic Inc.</b>', s['Body']), Paragraph('<b>Facturer à</b>', s['Body'])],
        [Paragraph('herbic.com', s['Small']),
         Paragraph(f'<b>{client.nom_ferme}</b>', s['Body'])],
        [Paragraph(f'Date: {facture.date_emission.strftime("%d/%m/%Y")}', s['Small']),
         Paragraph(f'{client.prenom} {client.nom}', s['Body'])],
        [Paragraph(f'Échéance: {facture.date_echeance.strftime("%d/%m/%Y") if facture.date_echeance else "-"}', s['Small']),
         Paragraph(f'{client.adresse}', s['Small'])],
        [Paragraph(f'Commande: CMD-{cmd.pk:05d}', s['Small']),
         Paragraph(f'{client.ville}, {client.code_postal}', s['Small'])],
    ]
    t = Table(info, colWidths=[250, 250])
    t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('TOPPADDING', (0, 0), (-1, -1), 2),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
    el.append(t)
    el.append(Spacer(1, 20))

    # Lignes
    data = [[Paragraph('Code', s['TH']), Paragraph('Produit', s['TH']),
             Paragraph('Qté', s['TH']), Paragraph('Prix unit.', s['TH']),
             Paragraph('Sous-total', s['TH'])]]

    for ligne in cmd.lignes.select_related('produit').all():
        st = ligne.sous_total
        data.append([
            Paragraph(ligne.produit.code, s['TD']),
            Paragraph(ligne.produit.nom, s['TDB']),
            Paragraph(str(int(ligne.quantite) if ligne.quantite == int(ligne.quantite) else ligne.quantite), s['TD']),
            Paragraph(_fmt(ligne.prix_unitaire) if ligne.prix_unitaire else '-', s['TD']),
            Paragraph(_fmt(st) if st else '-', s['TDB']),
        ])

    # Totaux
    data.append([Paragraph('', s['TD']), Paragraph('', s['TD']), Paragraph('', s['TD']),
                 Paragraph('Sous-total HT', s['Right']), Paragraph(_fmt(facture.sous_total_ht), s['RightB'])])
    data.append([Paragraph('', s['TD']), Paragraph('', s['TD']), Paragraph('', s['TD']),
                 Paragraph('TPS (5%)', s['Right']), Paragraph(_fmt(facture.montant_tps), s['Right'])])
    data.append([Paragraph('', s['TD']), Paragraph('', s['TD']), Paragraph('', s['TD']),
                 Paragraph('TVQ (9.975%)', s['Right']), Paragraph(_fmt(facture.montant_tvq), s['Right'])])
    data.append([Paragraph('', s['TD']), Paragraph('', s['TD']), Paragraph('', s['TD']),
                 Paragraph('<b>TOTAL TTC</b>', s['Right']), Paragraph(f'<b>{_fmt(facture.total_ttc)}</b>', s['RightB'])])

    t2 = Table(data, colWidths=[60, 200, 40, 80, 80])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GREEN),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
        ('BACKGROUND', (0, 1), (-1, -5), HexColor('#ffffff')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -5), [HexColor('#ffffff'), LIGHT]),
        ('BOX', (0, 0), (-1, -5), 0.5, BORDER),
        ('INNERGRID', (0, 0), (-1, -5), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('LINEABOVE', (3, -4), (-1, -4), 1, BORDER),
        ('LINEABOVE', (3, -1), (-1, -1), 2, GREEN),
    ]))
    el.append(t2)

    if facture.notes:
        el.append(Spacer(1, 15))
        el.append(Paragraph(f'<b>Notes:</b> {facture.notes}', s['Body']))

    el.append(Spacer(1, 30))
    el.append(Paragraph(f'Statut: {facture.get_statut_display()}', s['Small']))
    if facture.date_paiement:
        el.append(Paragraph(f'Payée le: {facture.date_paiement.strftime("%d/%m/%Y")}', s['Small']))

    doc.build(el)
    buf.seek(0)

    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{facture.numero}.pdf"'
    return response
