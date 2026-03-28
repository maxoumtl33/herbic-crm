"""
Script pour créer des données de démonstration.
Exécuter avec: python3 setup_demo_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'herbic_crm.settings')
django.setup()

from accounts.models import User
from clients.models import Client, Culture, ProduitArrosage, TypeCulture
from products.models import CategorieProduit, Produit, RecommandationProduit
from orders.models import Commande, LigneCommande
from tracking.models import SuiviPousse, StatistiqueCulture
from datetime import date, timedelta
from django.utils import timezone

vendeur = User.objects.get(username='vendeur1')
client_user = User.objects.get(username='client1')

# ============================================================
# PRODUITS
# ============================================================
print("--- Création des produits ---")

cat_sem_mais = CategorieProduit.objects.get(nom='Semences de maïs')
cat_sem_soya = CategorieProduit.objects.get(nom='Semences de soya')
cat_sem_ble = CategorieProduit.objects.get(nom='Semences de blé')
cat_herb = CategorieProduit.objects.get(nom='Herbicides')
cat_insect = CategorieProduit.objects.get(nom='Insecticides')
cat_fong = CategorieProduit.objects.get(nom='Fongicides')
cat_engrais = CategorieProduit.objects.get(nom='Engrais foliaires')
cat_bio = CategorieProduit.objects.get(nom='Biostimulants')
cat_additif = CategorieProduit.objects.get(nom='Additifs de pulvérisation')

produits_data = [
    # Semences maïs
    ('SEM-M001', 'Maïs Pioneer P9185AM', cat_sem_mais, 'Sac 80 000 grains', 320.00, 'maïs'),
    ('SEM-M002', 'Maïs Dekalb DKC35-88', cat_sem_mais, 'Sac 80 000 grains', 305.00, 'maïs'),
    ('SEM-M003', 'Maïs Elite E49A17', cat_sem_mais, 'Sac 80 000 grains', 290.00, 'maïs'),
    # Semences soya
    ('SEM-S001', 'Soya Prograin PRO 24X10', cat_sem_soya, 'Sac 140 000 grains', 85.00, 'soya'),
    ('SEM-S002', 'Soya Sevita SV5001GT', cat_sem_soya, 'Sac 140 000 grains', 78.00, 'soya'),
    ('SEM-S003', 'Soya Pioneer P09A78X', cat_sem_soya, 'Sac 140 000 grains', 92.00, 'soya'),
    # Semences blé
    ('SEM-B001', 'Blé Bolles (blé de printemps)', cat_sem_ble, 'Sac 25 kg', 42.00, 'blé'),
    ('SEM-B002', 'Blé Cardale (blé d\'automne)', cat_sem_ble, 'Sac 25 kg', 45.00, 'blé'),
    # Herbicides
    ('HERB-001', 'Roundup WeatherMAX', cat_herb, 'Bidon 10 L', 125.00, 'maïs,soya'),
    ('HERB-002', 'Engenia (Dicamba)', cat_herb, 'Bidon 10 L', 210.00, 'soya'),
    ('HERB-003', 'Callisto (Mésotrione)', cat_herb, 'Bidon 5 L', 185.00, 'maïs'),
    ('HERB-004', 'Infinity FX', cat_herb, 'Bidon 10 L', 155.00, 'blé,orge'),
    # Insecticides
    ('INSECT-001', 'Coragen (Chlorantraniliprole)', cat_insect, 'Bidon 3.78 L', 340.00, 'maïs,soya'),
    ('INSECT-002', 'Matador 120EC', cat_insect, 'Bidon 4 L', 165.00, 'maïs,soya,blé'),
    # Fongicides
    ('FONG-001', 'Prosaro XTR', cat_fong, 'Bidon 5 L', 275.00, 'blé,orge'),
    ('FONG-002', 'Miravis Neo', cat_fong, 'Bidon 5 L', 310.00, 'maïs'),
    ('FONG-003', 'Delaro Complete', cat_fong, 'Bidon 5 L', 255.00, 'soya'),
    # Engrais foliaires
    ('ENG-001', 'Foliaire N-P-K 20-20-20', cat_engrais, 'Sac 10 kg', 38.00, 'maïs,soya,blé'),
    ('ENG-002', 'Foliaire Calcium-Bore', cat_engrais, 'Bidon 10 L', 52.00, 'soya'),
    ('ENG-003', 'Manganèse foliaire 8%', cat_engrais, 'Bidon 10 L', 45.00, 'soya,blé'),
    # Biostimulants
    ('BIO-001', 'Stimulateur racinaire RhizoMax', cat_bio, 'Bidon 5 L', 120.00, 'maïs,soya'),
    ('BIO-002', 'Extrait d\'algues marines AgroKelp', cat_bio, 'Bidon 10 L', 95.00, 'maïs,soya,blé'),
    ('BIO-003', 'Acides humiques HumiGrow', cat_bio, 'Sac 20 kg', 75.00, 'maïs,soya,blé'),
    # Additifs pulvérisation
    ('ADD-001', 'Surfactant AgriSpread', cat_additif, 'Bidon 10 L', 55.00, ''),
    ('ADD-002', 'Anti-dérive DriftGuard', cat_additif, 'Bidon 10 L', 68.00, ''),
    ('ADD-003', 'Conditionneur d\'eau AquaFix', cat_additif, 'Bidon 20 L', 42.00, ''),
]

for code, nom, cat, fmt, prix, cultures in produits_data:
    p, created = Produit.objects.get_or_create(
        code=code,
        defaults={
            'nom': nom,
            'categorie': cat,
            'format_produit': fmt,
            'prix_unitaire': prix,
            'culture_recommandee': cultures,
            'en_stock': True,
        }
    )
    if created:
        print(f"  Produit: {nom}")

# Recommandations automatiques
print("\n--- Création des recommandations ---")
recos = [
    ('SEM-M001', 'mais', 10, 'Hybride populaire, excellent rendement zone 2800 UTM'),
    ('SEM-M002', 'mais', 8, 'Bon choix économique, bonne tolérance sécheresse'),
    ('HERB-001', 'mais', 9, 'Herbicide de base post-levée'),
    ('HERB-003', 'mais', 7, 'Excellent contrôle graminées annuelles'),
    ('FONG-002', 'mais', 5, 'Protection contre la fusariose'),
    ('BIO-001', 'mais', 6, 'Stimulation racinaire au semis'),
    ('SEM-S001', 'soya', 10, 'Variété hâtive, bon potentiel de rendement'),
    ('SEM-S003', 'soya', 8, 'Résistant phytophthora et SCN'),
    ('HERB-001', 'soya', 9, 'Désherbage pré-semis ou post-levée'),
    ('HERB-002', 'soya', 7, 'Contrôle mauvaises herbes résistantes'),
    ('FONG-003', 'soya', 6, 'Protection cercospora et rouille'),
    ('ENG-002', 'soya', 5, 'Apport calcium à la floraison'),
    ('SEM-B001', 'ble', 10, 'Blé de printemps, bonne qualité boulangère'),
    ('HERB-004', 'ble', 8, 'Herbicide large spectre pour céréales'),
    ('FONG-001', 'ble', 9, 'Protection fusariose de l\'épi'),
    ('ENG-003', 'ble', 6, 'Correction carence manganèse'),
]

for code, type_cult, prio, desc in recos:
    prod = Produit.objects.get(code=code)
    r, created = RecommandationProduit.objects.get_or_create(
        produit=prod, type_culture=TypeCulture.objects.get(code=type_cult),
        defaults={'priorite': prio, 'description': desc}
    )
    if created:
        print(f"  Reco: {prod.nom} -> {type_cult}")

# ============================================================
# CLIENTS ET FERMES
# ============================================================
print("\n--- Création des clients ---")

clients_data = [
    {
        'code': 'CLI-001', 'nom_ferme': 'Ferme Lavoie & Fils',
        'prenom': 'Pierre', 'nom': 'Lavoie',
        'adresse': '1250 Rang Saint-Joseph', 'ville': 'Saint-Hyacinthe',
        'code_postal': 'J2S 7B4', 'telephone': '450-555-0101',
        'cellulaire': '450-555-0102', 'courriel': 'pierre@fermelavoie.ca',
        'user': client_user,
        'cultures': [
            {'type': 'mais', 'champ': 'Champ Nord', 'acres': 150, 'semence': 'Pioneer P9185AM',
             'pop_visee': 34000, 'pop_reelle': 33200,
             'arrosages': [
                 ('Roundup WeatherMAX', '1.67 L/acre', 250.5, 'L', '2025-05-15'),
                 ('Callisto', '315 mL/acre', 47.25, 'L', '2025-06-10'),
                 ('RhizoMax', '200 mL/acre', 30.0, 'L', '2025-05-01'),
             ]},
            {'type': 'mais', 'champ': 'Champ Sud', 'acres': 100, 'semence': 'Dekalb DKC35-88',
             'pop_visee': 33000, 'pop_reelle': 32500,
             'arrosages': [
                 ('Roundup WeatherMAX', '1.67 L/acre', 167.0, 'L', '2025-05-16'),
                 ('Callisto', '315 mL/acre', 31.5, 'L', '2025-06-11'),
             ]},
            {'type': 'soya', 'champ': 'Champ Est', 'acres': 200, 'semence': 'Prograin PRO 24X10',
             'pop_visee': 155000, 'pop_reelle': 148000,
             'arrosages': [
                 ('Roundup WeatherMAX', '1.34 L/acre', 268.0, 'L', '2025-06-05'),
                 ('Engenia', '0.59 L/acre', 118.0, 'L', '2025-06-05'),
                 ('Delaro Complete', '800 mL/acre', 160.0, 'L', '2025-07-20'),
             ]},
        ],
    },
    {
        'code': 'CLI-002', 'nom_ferme': 'Ferme Beauregard',
        'prenom': 'Marc', 'nom': 'Beauregard',
        'adresse': '875 Chemin du Ruisseau', 'ville': 'Drummondville',
        'code_postal': 'J2A 3K1', 'telephone': '819-555-0201',
        'cellulaire': '819-555-0202', 'courriel': 'marc@fermebeauregard.ca',
        'user': None,
        'cultures': [
            {'type': 'mais', 'champ': 'Grande terre', 'acres': 300, 'semence': 'Elite E49A17',
             'pop_visee': 34000, 'pop_reelle': 33800,
             'arrosages': [
                 ('Roundup WeatherMAX', '1.67 L/acre', 501.0, 'L', '2025-05-14'),
                 ('Callisto', '315 mL/acre', 94.5, 'L', '2025-06-08'),
                 ('Miravis Neo', '500 mL/acre', 150.0, 'L', '2025-07-15'),
             ]},
            {'type': 'soya', 'champ': 'Terre basse', 'acres': 180, 'semence': 'Sevita SV5001GT',
             'pop_visee': 150000, 'pop_reelle': 145000,
             'arrosages': [
                 ('Roundup WeatherMAX', '1.34 L/acre', 241.2, 'L', '2025-06-03'),
             ]},
            {'type': 'ble', 'champ': 'Terre haute', 'acres': 80, 'semence': 'Bolles',
             'pop_visee': None, 'pop_reelle': None,
             'arrosages': [
                 ('Infinity FX', '0.41 L/acre', 32.8, 'L', '2025-05-25'),
                 ('Prosaro XTR', '0.8 L/acre', 64.0, 'L', '2025-06-20'),
             ]},
        ],
    },
    {
        'code': 'CLI-003', 'nom_ferme': 'Les Cultures Gagnon inc.',
        'prenom': 'Sylvie', 'nom': 'Gagnon',
        'adresse': '3200 Route 116', 'ville': 'Victoriaville',
        'code_postal': 'G6P 4S5', 'telephone': '819-555-0301',
        'cellulaire': '819-555-0302', 'courriel': 'sylvie@culturesgagnon.ca',
        'user': None,
        'cultures': [
            {'type': 'soya', 'champ': 'Lot A', 'acres': 250, 'semence': 'Pioneer P09A78X',
             'pop_visee': 160000, 'pop_reelle': 155000,
             'arrosages': [
                 ('Roundup WeatherMAX', '1.34 L/acre', 335.0, 'L', '2025-06-01'),
                 ('Engenia', '0.59 L/acre', 147.5, 'L', '2025-06-01'),
                 ('Foliaire Calcium-Bore', '2 L/acre', 500.0, 'L', '2025-07-10'),
                 ('Delaro Complete', '800 mL/acre', 200.0, 'L', '2025-07-18'),
             ]},
            {'type': 'mais', 'champ': 'Lot B', 'acres': 120, 'semence': 'Pioneer P9185AM',
             'pop_visee': 34500, 'pop_reelle': 33900,
             'arrosages': [
                 ('Roundup WeatherMAX', '1.67 L/acre', 200.4, 'L', '2025-05-18'),
                 ('AgroKelp', '1 L/acre', 120.0, 'L', '2025-06-15'),
             ]},
        ],
    },
    {
        'code': 'CLI-004', 'nom_ferme': 'Ferme du Boisé',
        'prenom': 'Luc', 'nom': 'Côté',
        'adresse': '560 Rang Saint-Antoine', 'ville': 'Nicolet',
        'code_postal': 'J3T 1A1', 'telephone': '819-555-0401',
        'cellulaire': '819-555-0402', 'courriel': 'luc@fermeduboise.ca',
        'user': None,
        'cultures': [
            {'type': 'mais', 'champ': 'Parcelle principale', 'acres': 200, 'semence': 'Dekalb DKC35-88',
             'pop_visee': 33500, 'pop_reelle': 32800,
             'arrosages': [
                 ('Roundup WeatherMAX', '1.67 L/acre', 334.0, 'L', '2025-05-12'),
                 ('Callisto', '315 mL/acre', 63.0, 'L', '2025-06-05'),
                 ('Coragen', '250 mL/acre', 50.0, 'L', '2025-06-25'),
             ]},
        ],
    },
    {
        'code': 'CLI-005', 'nom_ferme': 'Agri-Vallée SENC',
        'prenom': 'François', 'nom': 'Bergeron',
        'adresse': '1800 Boulevard Industriel', 'ville': 'Granby',
        'code_postal': 'J2G 8C9', 'telephone': '450-555-0501',
        'cellulaire': '450-555-0502', 'courriel': 'fbergeron@agrivallee.ca',
        'user': None,
        'cultures': [
            {'type': 'soya', 'champ': 'Champ 1', 'acres': 175, 'semence': 'Prograin PRO 24X10',
             'pop_visee': 155000, 'pop_reelle': 150000,
             'arrosages': [
                 ('Roundup WeatherMAX', '1.34 L/acre', 234.5, 'L', '2025-06-02'),
             ]},
            {'type': 'soya', 'champ': 'Champ 2', 'acres': 125, 'semence': 'Sevita SV5001GT',
             'pop_visee': 150000, 'pop_reelle': 146000,
             'arrosages': []},
            {'type': 'mais', 'champ': 'Champ 3', 'acres': 100, 'semence': 'Elite E49A17',
             'pop_visee': 34000, 'pop_reelle': 33500,
             'arrosages': [
                 ('Roundup WeatherMAX', '1.67 L/acre', 167.0, 'L', '2025-05-20'),
                 ('HumiGrow', '5 kg/acre', 500.0, 'kg', '2025-05-01'),
             ]},
        ],
    },
]

for cd in clients_data:
    client, created = Client.objects.get_or_create(
        code=cd['code'],
        defaults={
            'nom_ferme': cd['nom_ferme'],
            'prenom': cd['prenom'],
            'nom': cd['nom'],
            'adresse': cd['adresse'],
            'ville': cd['ville'],
            'code_postal': cd['code_postal'],
            'telephone': cd['telephone'],
            'cellulaire': cd['cellulaire'],
            'courriel': cd['courriel'],
            'vendeur': vendeur,
            'user': cd['user'],
        }
    )
    if created:
        print(f"  Client: {cd['nom_ferme']}")

        for cult_data in cd['cultures']:
            culture = Culture.objects.create(
                client=client,
                type_culture=TypeCulture.objects.get(code=cult_data['type']),
                nom_champ=cult_data['champ'],
                superficie_acres=cult_data['acres'],
                semence=cult_data['semence'],
                population_visee=cult_data['pop_visee'],
                population_reelle=cult_data['pop_reelle'],
                annee=2025,
            )
            print(f"    Culture: {cult_data['type']} - {cult_data['champ']} ({cult_data['acres']} acres)")

            for arr in cult_data['arrosages']:
                ProduitArrosage.objects.create(
                    culture=culture,
                    nom_produit=arr[0],
                    dose=arr[1],
                    quantite_totale=arr[2],
                    unite=arr[3],
                    date_application=date.fromisoformat(arr[4]) if arr[4] else None,
                )

# ============================================================
# COMMANDES
# ============================================================
print("\n--- Création des commandes ---")

client1 = Client.objects.get(code='CLI-001')
client2 = Client.objects.get(code='CLI-002')
client3 = Client.objects.get(code='CLI-003')
client4 = Client.objects.get(code='CLI-004')
client5 = Client.objects.get(code='CLI-005')
magasin_user = User.objects.get(username='magasin1')

# Commande livrée
cmd1 = Commande.objects.create(
    client=client1, vendeur=vendeur, preparateur=magasin_user,
    statut='livree', notes='Livraison effectuée le 28 avril',
    date_livraison_prevue=date(2025, 4, 28),
)
for code, qty in [('SEM-M001', 5), ('SEM-S001', 8), ('HERB-001', 3), ('BIO-001', 2)]:
    p = Produit.objects.get(code=code)
    LigneCommande.objects.create(commande=cmd1, produit=p, quantite=qty, prix_unitaire=p.prix_unitaire)
print(f"  CMD-{cmd1.pk:05d} Ferme Lavoie (livrée)")

# Commande prête
cmd2 = Commande.objects.create(
    client=client2, vendeur=vendeur, preparateur=magasin_user,
    statut='prete', notes='Client passera chercher',
    date_livraison_prevue=date(2025, 5, 5),
)
for code, qty in [('SEM-M003', 10), ('HERB-001', 5), ('HERB-003', 2), ('FONG-002', 1), ('ADD-001', 2)]:
    p = Produit.objects.get(code=code)
    LigneCommande.objects.create(commande=cmd2, produit=p, quantite=qty, prix_unitaire=p.prix_unitaire)
print(f"  CMD-{cmd2.pk:05d} Ferme Beauregard (prête)")

# Commande en préparation
cmd3 = Commande.objects.create(
    client=client3, vendeur=vendeur, preparateur=magasin_user,
    statut='en_preparation',
    date_livraison_prevue=date(2025, 5, 10),
)
for code, qty in [('SEM-S003', 12), ('HERB-001', 4), ('HERB-002', 3), ('ENG-002', 5), ('ADD-002', 2)]:
    p = Produit.objects.get(code=code)
    LigneCommande.objects.create(commande=cmd3, produit=p, quantite=qty, prix_unitaire=p.prix_unitaire)
print(f"  CMD-{cmd3.pk:05d} Cultures Gagnon (en préparation)")

# Commande nouvelle
cmd4 = Commande.objects.create(
    client=client4, vendeur=vendeur,
    statut='nouvelle', notes='Urgent - semis prévu la semaine prochaine',
    date_livraison_prevue=date(2025, 5, 8),
)
for code, qty in [('SEM-M002', 7), ('HERB-001', 3), ('INSECT-001', 1), ('BIO-002', 2)]:
    p = Produit.objects.get(code=code)
    LigneCommande.objects.create(commande=cmd4, produit=p, quantite=qty, prix_unitaire=p.prix_unitaire)
print(f"  CMD-{cmd4.pk:05d} Ferme du Boisé (nouvelle)")

# Commande en livraison
cmd5 = Commande.objects.create(
    client=client5, vendeur=vendeur, preparateur=magasin_user,
    statut='en_livraison',
    date_livraison_prevue=date(2025, 5, 3),
)
for code, qty in [('SEM-S001', 6), ('SEM-S002', 5), ('SEM-M003', 3), ('HERB-001', 4), ('BIO-003', 3), ('ADD-003', 2)]:
    p = Produit.objects.get(code=code)
    LigneCommande.objects.create(commande=cmd5, produit=p, quantite=qty, prix_unitaire=p.prix_unitaire)
print(f"  CMD-{cmd5.pk:05d} Agri-Vallée (en livraison)")

# ============================================================
# SUIVIS DE POUSSE
# ============================================================
print("\n--- Création des suivis de pousse ---")

culture_mais_nord = Culture.objects.get(client=client1, nom_champ='Champ Nord')
culture_soya_est = Culture.objects.get(client=client1, nom_champ='Champ Est')

suivis_mais = [
    (date(2025, 5, 10), 'VE - Émergence', 3.0, 33200, 'bon', '', 'Levée uniforme'),
    (date(2025, 5, 20), 'V2 - 2 feuilles', 12.0, 33100, 'bon', '', 'Bonne vigueur'),
    (date(2025, 5, 30), 'V4 - 4 feuilles', 28.0, 33000, 'excellent', '', 'Croissance rapide, bon départ'),
    (date(2025, 6, 10), 'V6 - 6 feuilles', 55.0, 32900, 'excellent', '', 'Application Callisto effectuée'),
    (date(2025, 6, 25), 'V10 - 10 feuilles', 95.0, 32800, 'bon', 'Légère pression chrysomèle', ''),
    (date(2025, 7, 10), 'VT - Panicule', 180.0, 32700, 'bon', '', 'Pollinisation en cours'),
    (date(2025, 7, 25), 'R2 - Ampoule', 210.0, None, 'bon', '', 'Grain en formation'),
]

for d, stade, h, dens, etat, prob, notes in suivis_mais:
    SuiviPousse.objects.create(
        culture=culture_mais_nord, date_observation=d,
        stade_croissance=stade, hauteur_cm=h,
        densite_plants=dens, etat_general=etat,
        problemes_observes=prob, notes=notes, observateur=vendeur,
    )
print(f"  {len(suivis_mais)} observations - Maïs Champ Nord (Ferme Lavoie)")

StatistiqueCulture.objects.get_or_create(
    culture=culture_mais_nord,
    defaults={
        'rendement_estime': 185.0,
        'rendement_reel': None,
        'taux_germination': 97.6,
        'cout_total_intrants': 18750.00,
        'date_semis': date(2025, 5, 1),
        'date_recolte': None,
    }
)
print("  Stats maïs Champ Nord créées")

suivis_soya = [
    (date(2025, 6, 12), 'VE - Émergence', 3.0, 148000, 'bon', '', 'Bonne levée'),
    (date(2025, 6, 22), 'V2 - 2e trifolié', 10.0, 147500, 'bon', '', ''),
    (date(2025, 7, 5), 'V4 - 4e trifolié', 22.0, 147000, 'bon', '', 'Bon développement'),
    (date(2025, 7, 20), 'R1 - Début floraison', 45.0, None, 'excellent', '', 'Application Delaro Complete'),
    (date(2025, 8, 5), 'R3 - Début gousse', 60.0, None, 'bon', 'Quelques taches cercospora', ''),
]

for d, stade, h, dens, etat, prob, notes in suivis_soya:
    SuiviPousse.objects.create(
        culture=culture_soya_est, date_observation=d,
        stade_croissance=stade, hauteur_cm=h,
        densite_plants=dens, etat_general=etat,
        problemes_observes=prob, notes=notes, observateur=vendeur,
    )
print(f"  {len(suivis_soya)} observations - Soya Champ Est (Ferme Lavoie)")

StatistiqueCulture.objects.get_or_create(
    culture=culture_soya_est,
    defaults={
        'rendement_estime': 48.0,
        'taux_germination': 95.5,
        'cout_total_intrants': 22400.00,
        'date_semis': date(2025, 6, 1),
    }
)
print("  Stats soya Champ Est créées")

print("\n=== Données de démonstration créées avec succès! ===")
print(f"  {Client.objects.count()} clients")
print(f"  {Culture.objects.count()} cultures")
print(f"  {Produit.objects.count()} produits")
print(f"  {Commande.objects.count()} commandes")
print(f"  {SuiviPousse.objects.count()} suivis de pousse")
