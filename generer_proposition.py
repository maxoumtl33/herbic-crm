"""
Génère la proposition commerciale Herbic CRM en PDF.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from datetime import date

GREEN = HexColor('#2e7d32')
GREEN_LIGHT = HexColor('#4caf50')
GREEN_BG = HexColor('#e8f5e9')
DARK = HexColor('#1a1a2e')
GRAY = HexColor('#64748b')
LIGHT_GRAY = HexColor('#f4f6f9')
BORDER = HexColor('#e2e8f0')

output = '/Users/maximegarcia/Desktop/Proposition_Herbic_CRM.pdf'
doc = SimpleDocTemplate(
    output,
    pagesize=letter,
    topMargin=0.6*inch,
    bottomMargin=0.6*inch,
    leftMargin=0.75*inch,
    rightMargin=0.75*inch,
)

styles = getSampleStyleSheet()

# Custom styles
styles.add(ParagraphStyle(
    'DocTitle', parent=styles['Title'],
    fontSize=26, textColor=GREEN, spaceAfter=4,
    fontName='Helvetica-Bold', leading=30,
))
styles.add(ParagraphStyle(
    'DocSubtitle', parent=styles['Normal'],
    fontSize=12, textColor=GRAY, spaceAfter=20,
    fontName='Helvetica',
))
styles.add(ParagraphStyle(
    'SectionTitle', parent=styles['Heading1'],
    fontSize=15, textColor=GREEN, spaceBefore=24, spaceAfter=10,
    fontName='Helvetica-Bold', borderPadding=(0, 0, 4, 0),
))
styles.add(ParagraphStyle(
    'SubSection', parent=styles['Heading2'],
    fontSize=11, textColor=DARK, spaceBefore=14, spaceAfter=6,
    fontName='Helvetica-Bold',
))
styles.add(ParagraphStyle(
    'BodyText2', parent=styles['Normal'],
    fontSize=9.5, textColor=DARK, spaceAfter=6,
    fontName='Helvetica', leading=14,
))
styles.add(ParagraphStyle(
    'BulletItem', parent=styles['Normal'],
    fontSize=9.5, textColor=DARK, spaceAfter=3,
    fontName='Helvetica', leading=14,
    leftIndent=16, bulletIndent=4,
))
styles.add(ParagraphStyle(
    'Small', parent=styles['Normal'],
    fontSize=8, textColor=GRAY,
    fontName='Helvetica',
))
styles.add(ParagraphStyle(
    'PriceHighlight', parent=styles['Normal'],
    fontSize=20, textColor=GREEN, fontName='Helvetica-Bold',
    alignment=TA_CENTER, spaceAfter=4,
))
styles.add(ParagraphStyle(
    'PriceLabel', parent=styles['Normal'],
    fontSize=9, textColor=GRAY, fontName='Helvetica',
    alignment=TA_CENTER, spaceAfter=0,
))
styles.add(ParagraphStyle(
    'TableHeader', parent=styles['Normal'],
    fontSize=8.5, textColor=white, fontName='Helvetica-Bold',
    leading=12,
))
styles.add(ParagraphStyle(
    'TableCell', parent=styles['Normal'],
    fontSize=9, textColor=DARK, fontName='Helvetica',
    leading=13,
))
styles.add(ParagraphStyle(
    'TableCellBold', parent=styles['Normal'],
    fontSize=9, textColor=DARK, fontName='Helvetica-Bold',
    leading=13,
))
styles.add(ParagraphStyle(
    'Footer', parent=styles['Normal'],
    fontSize=8, textColor=GRAY, fontName='Helvetica',
    alignment=TA_CENTER,
))

elements = []

# ============================================================
# HEADER
# ============================================================
today = date.today().strftime('%d/%m/%Y')

elements.append(Spacer(1, 10))
elements.append(Paragraph('Proposition commerciale', styles['DocTitle']))
elements.append(Paragraph('Plateforme CRM Herbic - Suivi client, gestion des commandes et recommandations intelligentes', styles['DocSubtitle']))

# Info box
info_data = [
    [Paragraph('<b>Préparé pour :</b>', styles['TableCell']),
     Paragraph('Herbic Inc.', styles['TableCell']),
     Paragraph(f'<b>Date :</b>', styles['TableCell']),
     Paragraph(today, styles['TableCell'])],
    [Paragraph('<b>Préparé par :</b>', styles['TableCell']),
     Paragraph('Maxime Garcia', styles['TableCell']),
     Paragraph('', styles['TableCell']),
     Paragraph('-', styles['TableCell'])],
]
info_table = Table(info_data, colWidths=[90, 180, 70, 120])
info_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GRAY),
    ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
]))
elements.append(info_table)
elements.append(Spacer(1, 6))
elements.append(HRFlowable(width='100%', thickness=2, color=GREEN, spaceAfter=6))

# ============================================================
# CONTEXTE
# ============================================================
elements.append(Paragraph('1. Contexte du projet', styles['SectionTitle']))
elements.append(Paragraph(
    "Herbic Inc. souhaite se doter d'une plateforme CRM sur mesure pour optimiser "
    "le suivi de ses clients agricoles, la gestion des commandes et la recommandation "
    "de produits. L'objectif est de fournir aux vendeurs terrain un outil mobile intuitif, "
    "au magasin un workflow de préparation efficace, et à la direction une vue d'ensemble "
    "complète avec des outils d'administration.",
    styles['BodyText2']
))
elements.append(Paragraph(
    "La plateforme s'intègrera au site web existant (herbic.com, WordPress + WooCommerce) "
    "via un sous-domaine dédié (crm.herbic.com) avec base de données sécurisée.",
    styles['BodyText2']
))

# ============================================================
# FONCTIONNALITÉS
# ============================================================
elements.append(Paragraph('2. Fonctionnalités livrées', styles['SectionTitle']))

# Vendeur
elements.append(Paragraph('Rôle Vendeur (interface mobile terrain)', styles['SubSection']))
features_vendeur = [
    "Dashboard personnalisé avec clients assignés, commandes, livraisons à faire",
    "Recherche client rapide (nom, ferme, ville, code)",
    "Fiche client complète : ferme, cultures, superficies, semences, populations, produits d'arrosage avec doses",
    "Actions rapides sur mobile : appeler le client, GPS vers la ferme, passer commande",
    "Création de nouveau client avec toutes ses informations",
    "Passage de commande pour un client (choix produits, quantités, date livraison)",
    "Confirmation de livraison en un clic",
    "Suivi de pousse : observations terrain (stade, hauteur, densité, état, photos)",
    "Statistiques de culture (germination, rendement, coûts intrants)",
    "Recommandations intelligentes de produits sur chaque fiche client",
]
for f in features_vendeur:
    elements.append(Paragraph(f'\u2022  {f}', styles['BulletItem']))

# Magasin
elements.append(Paragraph('Rôle Magasin (préparation des commandes)', styles['SubSection']))
features_magasin = [
    "Dashboard avec compteurs temps réel : à traiter, en préparation, prêtes, en livraison",
    "Prise en charge des nouvelles commandes",
    "Préparation produit par produit avec jauge de progression visuelle",
    "Passage automatique au statut 'Prête' quand tout est coché",
    "Envoi en livraison et confirmation en un clic",
    "Traçabilité complète : qui a préparé quoi et quand",
]
for f in features_magasin:
    elements.append(Paragraph(f'\u2022  {f}', styles['BulletItem']))

# Client
elements.append(Paragraph('Rôle Client', styles['SubSection']))
features_client = [
    "Espace personnel : infos ferme, cultures, vendeur assigné",
    "Consultation des commandes et suivi de statut en temps réel",
    "Possibilité de passer une commande en ligne",
    "Consultation du suivi de pousse de ses cultures",
]
for f in features_client:
    elements.append(Paragraph(f'\u2022  {f}', styles['BulletItem']))

# Directeur
elements.append(Paragraph('Rôle Directeur (administration complète)', styles['SubSection']))
features_directeur = [
    "Dashboard avec KPIs globaux (clients, commandes, charge vendeurs)",
    "Gestion des utilisateurs et des rôles",
    "Catalogue produits complet : CRUD semences, pesticides, engrais, biostimulants, additifs",
    "Gestion des catégories de produits",
    "Configuration des recommandations : produit, culture, saison, dose, complémentarité, problèmes ciblés",
    "Accès à toutes les fiches clients, commandes et suivis",
]
for f in features_directeur:
    elements.append(Paragraph(f'\u2022  {f}', styles['BulletItem']))

# Moteur de recommandation
elements.append(Paragraph('Moteur de recommandation intelligent', styles['SubSection']))
elements.append(Paragraph(
    "Le système analyse automatiquement le profil de chaque client et recommande les "
    "produits les plus pertinents avec calcul de quantités estimées. Sept critères de scoring :",
    styles['BodyText2']
))

reco_data = [
    [Paragraph('<b>Critère</b>', styles['TableHeader']),
     Paragraph('<b>Description</b>', styles['TableHeader'])],
    [Paragraph('Type de culture', styles['TableCellBold']),
     Paragraph('Maïs, soya, blé... chaque produit est associé à ses cultures cibles', styles['TableCell'])],
    [Paragraph('Saison actuelle', styles['TableCellBold']),
     Paragraph('Pré-semis, semis, post-levée, floraison, récolte - les produits pertinents remontent', styles['TableCell'])],
    [Paragraph('Déjà acheté', styles['TableCellBold']),
     Paragraph('Les produits déjà commandés cette saison sont rétrogradés pour éviter les doublons', styles['TableCell'])],
    [Paragraph('Déjà appliqué', styles['TableCellBold']),
     Paragraph("Les produits déjà épandus sur la culture sont identifiés et rétrogradés", styles['TableCell'])],
    [Paragraph('Complémentarité', styles['TableCellBold']),
     Paragraph("Si le client a acheté la semence X, le fongicide compatible Y est priorisé", styles['TableCell'])],
    [Paragraph('Problèmes terrain', styles['TableCellBold']),
     Paragraph("Les observations du suivi (chrysomèle, cercospora...) font remonter les traitements ciblés", styles['TableCell'])],
    [Paragraph('Écart population', styles['TableCellBold']),
     Paragraph("Si la population réelle est sous la cible, les biostimulants sont recommandés", styles['TableCell'])],
]
reco_table = Table(reco_data, colWidths=[110, 350])
reco_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), GREEN),
    ('TEXTCOLOR', (0, 0), (-1, 0), white),
    ('BACKGROUND', (0, 1), (-1, -1), white),
    ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GRAY]),
]))
elements.append(reco_table)

# ============================================================
# INTÉGRATION
# ============================================================
elements.append(Paragraph('3. Intégration et infrastructure', styles['SectionTitle']))

elements.append(Paragraph('Architecture proposée', styles['SubSection']))
elements.append(Paragraph(
    "Le CRM sera déployé en sous-domaine (crm.herbic.com) sur un serveur dédié, "
    "séparé du site WordPress existant. Cette approche garantit :",
    styles['BodyText2']
))
for f in [
    "Aucun risque d'impact sur le site herbic.com existant",
    "Déploiement et mises à jour indépendantes",
    "Performance optimale (serveur dédié au CRM)",
    "Possibilité de synchronisation avec WooCommerce via API",
]:
    elements.append(Paragraph(f'\u2022  {f}', styles['BulletItem']))

elements.append(Paragraph('Base de données sécurisée', styles['SubSection']))
elements.append(Paragraph(
    "PostgreSQL hébergé sur serveur géré (Managed Database) avec :",
    styles['BodyText2']
))
for f in [
    "Sauvegardes automatiques quotidiennes",
    "Connexion chiffrée SSL/TLS",
    "Accès restreint par pare-feu (CRM seulement)",
    "Serveur au Canada (conformité données canadiennes)",
]:
    elements.append(Paragraph(f'\u2022  {f}', styles['BulletItem']))

elements.append(Paragraph('Mise en production', styles['SubSection']))
for f in [
    "Configuration du serveur de production",
    "Migration de la base de données SQLite vers PostgreSQL",
    "Configuration du domaine crm.herbic.com avec certificat SSL",
    "Import des données réelles (clients, produits) depuis WooCommerce",
    "Lien dans le menu du site WordPress vers le CRM",
    "Formation des utilisateurs (1 à 2 heures par rôle)",
    "Tests et validation avant mise en ligne",
]:
    elements.append(Paragraph(f'\u2022  {f}', styles['BulletItem']))

# ============================================================
# TARIFICATION
# ============================================================
elements.append(Paragraph('4. Tarification', styles['SectionTitle']))

# Price cards
price_data = [
    [Paragraph('<b>Phase</b>', styles['TableHeader']),
     Paragraph('<b>Détail</b>', styles['TableHeader']),
     Paragraph('<b>Prix</b>', styles['TableHeader'])],
    [Paragraph('Phase 1\nDéveloppement CRM', styles['TableCellBold']),
     Paragraph(
         "Application complète avec les 4 rôles (vendeur, magasin, client, directeur), "
         "gestion clients/fermes/cultures, commandes avec workflow complet, "
         "suivi de pousse, moteur de recommandation intelligent, "
         "interface mobile vendeur, interface préparation magasin, "
         "administration directeur, catalogue produits et recommandations.",
         styles['TableCell']),
     Paragraph('<b>4 000 $</b>', styles['TableCellBold'])],
    [Paragraph('Phase 2\nIntégration +\nMise en production', styles['TableCellBold']),
     Paragraph(
         "Serveur de production sécurisé, base de données PostgreSQL, "
         "domaine crm.herbic.com avec SSL, import données depuis WooCommerce, "
         "formation des utilisateurs, tests et validation.",
         styles['TableCell']),
     Paragraph('<b>3 000 $</b>', styles['TableCellBold'])],
]
price_table = Table(price_data, colWidths=[100, 290, 70])
price_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), GREEN),
    ('TEXTCOLOR', (0, 0), (-1, 0), white),
    ('BACKGROUND', (0, 1), (-1, -1), white),
    ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('ALIGN', (2, 0), (2, -1), 'CENTER'),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GRAY]),
]))
elements.append(price_table)
elements.append(Spacer(1, 12))

# Total box
total_data = [
    [Paragraph('TOTAL PROJET', styles['TableHeader']),
     Paragraph('<b>7 000 $ CAD</b>', styles['TableHeader'])],
]
total_table = Table(total_data, colWidths=[360, 100])
total_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), GREEN),
    ('TEXTCOLOR', (0, 0), (-1, -1), white),
    ('ALIGN', (1, 0), (1, 0), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ('BOX', (0, 0), (-1, -1), 0, GREEN),
    ('ROUNDEDCORNERS', [6, 6, 6, 6]),
]))
elements.append(total_table)
elements.append(Spacer(1, 16))

# Mensuel
elements.append(Paragraph('Forfait mensuel récurrent', styles['SubSection']))
mensuel_data = [
    [Paragraph('<b>Forfait mensuel</b>', styles['TableHeader']),
     Paragraph('<b>Inclus</b>', styles['TableHeader']),
     Paragraph('<b>Prix</b>', styles['TableHeader'])],
    [Paragraph('Maintenance\net hébergement', styles['TableCellBold']),
     Paragraph(
         '\u2022  Hébergement serveur + base de données sécurisée\n'
         '\u2022  Sauvegardes automatiques quotidiennes\n'
         '\u2022  Mises à jour de sécurité\n'
         '\u2022  Corrections de bugs\n'
         '\u2022  Changements et améliorations sur demande\n'
         '\u2022  Support par courriel',
         styles['TableCell']),
     Paragraph('<b>250 $/mois</b>', styles['TableCellBold'])],
]
mensuel_table = Table(mensuel_data, colWidths=[100, 290, 70])
mensuel_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), GREEN),
    ('TEXTCOLOR', (0, 0), (-1, 0), white),
    ('BACKGROUND', (0, 1), (-1, -1), white),
    ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('ALIGN', (2, 0), (2, -1), 'CENTER'),
]))
elements.append(mensuel_table)

# ============================================================
# WORKFLOW
# ============================================================
elements.append(Paragraph('5. Workflow des commandes', styles['SectionTitle']))

workflow_data = [
    [Paragraph('<b>Étape</b>', styles['TableHeader']),
     Paragraph('<b>Qui</b>', styles['TableHeader']),
     Paragraph('<b>Action</b>', styles['TableHeader'])],
    [Paragraph('1', styles['TableCellBold']),
     Paragraph('Vendeur', styles['TableCell']),
     Paragraph("Passe la commande pour le client depuis le terrain (ou le client commande lui-même)", styles['TableCell'])],
    [Paragraph('2', styles['TableCellBold']),
     Paragraph('Magasin', styles['TableCell']),
     Paragraph("Reçoit la commande, la prend en charge et commence la préparation", styles['TableCell'])],
    [Paragraph('3', styles['TableCellBold']),
     Paragraph('Magasin', styles['TableCell']),
     Paragraph("Coche chaque produit un par un (jauge de progression). Statut 'Prête' automatique.", styles['TableCell'])],
    [Paragraph('4', styles['TableCellBold']),
     Paragraph('Magasin', styles['TableCell']),
     Paragraph("Envoie la commande en livraison", styles['TableCell'])],
    [Paragraph('5', styles['TableCellBold']),
     Paragraph('Vendeur', styles['TableCell']),
     Paragraph("Livre le client et confirme la livraison depuis son téléphone", styles['TableCell'])],
]
workflow_table = Table(workflow_data, colWidths=[40, 70, 350])
workflow_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), GREEN),
    ('TEXTCOLOR', (0, 0), (-1, 0), white),
    ('BACKGROUND', (0, 1), (-1, -1), white),
    ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GRAY]),
]))
elements.append(workflow_table)

# ============================================================
# ÉCHÉANCIER
# ============================================================
elements.append(Paragraph('6. Échéancier', styles['SectionTitle']))

echeance_data = [
    [Paragraph('<b>Étape</b>', styles['TableHeader']),
     Paragraph('<b>Durée estimée</b>', styles['TableHeader'])],
    [Paragraph('Validation de la proposition', styles['TableCell']),
     Paragraph("À convenir", styles['TableCell'])],
    [Paragraph('Phase 1 - Développement CRM', styles['TableCell']),
     Paragraph("Complété (prêt à tester)", styles['TableCell'])],
    [Paragraph('Tests et ajustements avec le client', styles['TableCell']),
     Paragraph("1 à 2 semaines", styles['TableCell'])],
    [Paragraph('Phase 2 - Intégration et mise en production', styles['TableCell']),
     Paragraph("1 à 2 semaines", styles['TableCell'])],
    [Paragraph('Formation des utilisateurs', styles['TableCell']),
     Paragraph("1 à 2 jours", styles['TableCell'])],
    [Paragraph('Mise en ligne', styles['TableCell']),
     Paragraph("Immédiat après validation", styles['TableCell'])],
]
echeance_table = Table(echeance_data, colWidths=[300, 160])
echeance_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), GREEN),
    ('TEXTCOLOR', (0, 0), (-1, 0), white),
    ('BACKGROUND', (0, 1), (-1, -1), white),
    ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GRAY]),
]))
elements.append(echeance_table)

# ============================================================
# ACCÈS DÉMO
# ============================================================
elements.append(Paragraph('7. Accès à la démonstration', styles['SectionTitle']))
elements.append(Paragraph(
    "Une version de démonstration est disponible avec des données fictives pour tester "
    "l'ensemble des fonctionnalités :",
    styles['BodyText2']
))

demo_data = [
    [Paragraph('<b>Rôle</b>', styles['TableHeader']),
     Paragraph('<b>Utilisateur</b>', styles['TableHeader']),
     Paragraph('<b>Mot de passe</b>', styles['TableHeader']),
     Paragraph('<b>Accès</b>', styles['TableHeader'])],
    [Paragraph('Directeur', styles['TableCellBold']),
     Paragraph('admin', styles['TableCell']),
     Paragraph('admin123', styles['TableCell']),
     Paragraph('Accès complet + administration', styles['TableCell'])],
    [Paragraph('Vendeur', styles['TableCellBold']),
     Paragraph('vendeur1', styles['TableCell']),
     Paragraph('vendeur123', styles['TableCell']),
     Paragraph('Clients, commandes, suivi terrain', styles['TableCell'])],
    [Paragraph('Magasin', styles['TableCellBold']),
     Paragraph('magasin1', styles['TableCell']),
     Paragraph('magasin123', styles['TableCell']),
     Paragraph('Préparation et suivi commandes', styles['TableCell'])],
    [Paragraph('Client', styles['TableCellBold']),
     Paragraph('client1', styles['TableCell']),
     Paragraph('client123', styles['TableCell']),
     Paragraph('Espace client personnel', styles['TableCell'])],
]
demo_table = Table(demo_data, colWidths=[70, 80, 80, 230])
demo_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), GREEN),
    ('TEXTCOLOR', (0, 0), (-1, 0), white),
    ('BACKGROUND', (0, 1), (-1, -1), white),
    ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GRAY]),
]))
elements.append(demo_table)
elements.append(Spacer(1, 8))
elements.append(Paragraph(
    '<b>URL de démonstration :</b> https://maxoufaya33.pythonanywhere.com/',
    styles['BodyText2']
))
elements.append(Paragraph(
    "Tester sur téléphone avec le compte vendeur pour voir l'interface mobile optimisée.",
    styles['Small']
))

# ============================================================
# FOOTER
# ============================================================
elements.append(Spacer(1, 30))
elements.append(HRFlowable(width='100%', thickness=1, color=BORDER, spaceAfter=8))
elements.append(Paragraph(
    'Maxime Garcia | maxime-garcia@windowslive.com',
    styles['Footer']
))

# Build PDF
doc.build(elements)
print(f'PDF généré: {output}')
