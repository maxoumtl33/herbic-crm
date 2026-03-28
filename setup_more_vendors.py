"""
Crée des vendeurs supplémentaires avec clients, commandes et livraisons.
Exécuter avec: python3 setup_more_vendors.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'herbic_crm.settings')
django.setup()

from accounts.models import User
from clients.models import Client, Culture, TypeCulture
from products.models import Produit
from orders.models import Commande, LigneCommande, Facture
from datetime import date, timedelta
from django.utils import timezone

# === VENDEURS ===
vendeurs_data = [
    ('vendeur2', 'vendeur123', 'Sophie', 'Bouchard'),
    ('vendeur3', 'vendeur123', 'Martin', 'Pelletier'),
]

vendeurs = {}
for username, pwd, prenom, nom in vendeurs_data:
    v, created = User.objects.get_or_create(
        username=username,
        defaults={'first_name': prenom, 'last_name': nom, 'role': 'vendeur'}
    )
    if created:
        v.set_password(pwd)
        v.save()
        print(f"Vendeur créé: {prenom} {nom} ({username})")
    vendeurs[username] = v

# Aussi récupérer vendeur1
vendeurs['vendeur1'] = User.objects.get(username='vendeur1')

tc_mais = TypeCulture.objects.get(code='mais')
tc_soya = TypeCulture.objects.get(code='soya')
tc_ble = TypeCulture.objects.get(code='ble')

# === CLIENTS POUR VENDEUR 2 (Sophie Bouchard) ===
v2_clients = [
    {
        'code': 'CLI-006', 'nom_ferme': 'Ferme des Érables', 'prenom': 'Alain', 'nom': 'Morin',
        'adresse': '450 Rang des Pins', 'ville': 'Bécancour', 'code_postal': 'G9H 2K3',
        'telephone': '819-555-0601', 'cellulaire': '819-555-0602',
        'cultures': [('mais', 220), ('soya', 160)],
    },
    {
        'code': 'CLI-007', 'nom_ferme': 'Agri-Pro Dupont', 'prenom': 'Caroline', 'nom': 'Dupont',
        'adresse': '1100 Route 132', 'ville': 'Sorel-Tracy', 'code_postal': 'J3P 5N5',
        'telephone': '450-555-0701', 'cellulaire': '450-555-0702',
        'cultures': [('mais', 350), ('ble', 120)],
    },
    {
        'code': 'CLI-008', 'nom_ferme': 'Les Grains Dorés inc.', 'prenom': 'René', 'nom': 'Fortin',
        'adresse': '2800 Chemin de la Rivière', 'ville': 'Trois-Rivières', 'code_postal': 'G9A 5E1',
        'telephone': '819-555-0801', 'cellulaire': '819-555-0802',
        'cultures': [('soya', 280), ('mais', 190)],
    },
]

# === CLIENTS POUR VENDEUR 3 (Martin Pelletier) ===
v3_clients = [
    {
        'code': 'CLI-009', 'nom_ferme': 'Ferme Saint-Louis', 'prenom': 'Isabelle', 'nom': 'Roy',
        'adresse': '675 Rang Saint-Louis', 'ville': 'Lotbinière', 'code_postal': 'G0S 1S0',
        'telephone': '418-555-0901', 'cellulaire': '418-555-0902',
        'cultures': [('mais', 180), ('soya', 140), ('ble', 60)],
    },
    {
        'code': 'CLI-010', 'nom_ferme': 'Domaine Agricole Plante', 'prenom': 'Yves', 'nom': 'Plante',
        'adresse': '900 Route Kennedy', 'ville': 'Lévis', 'code_postal': 'G6V 6R2',
        'telephone': '418-555-1001', 'cellulaire': '418-555-1002',
        'cultures': [('soya', 320), ('mais', 100)],
    },
]

def create_clients_and_cultures(clients_data, vendeur):
    created_clients = []
    for cd in clients_data:
        client, created = Client.objects.get_or_create(
            code=cd['code'],
            defaults={
                'nom_ferme': cd['nom_ferme'], 'prenom': cd['prenom'], 'nom': cd['nom'],
                'adresse': cd['adresse'], 'ville': cd['ville'], 'code_postal': cd['code_postal'],
                'telephone': cd['telephone'], 'cellulaire': cd['cellulaire'],
                'vendeur': vendeur,
            }
        )
        if created:
            print(f"  Client: {cd['nom_ferme']} -> {vendeur.get_full_name()}")
            for tc_code, acres in cd['cultures']:
                tc = TypeCulture.objects.get(code=tc_code)
                Culture.objects.create(
                    client=client, type_culture=tc, nom_champ=f'Parcelle {tc.nom}',
                    superficie_acres=acres, annee=2025,
                    population_visee=34000 if tc_code == 'mais' else 150000 if tc_code == 'soya' else None,
                    population_reelle=33200 if tc_code == 'mais' else 146000 if tc_code == 'soya' else None,
                )
        created_clients.append(client)
    return created_clients

print("\n--- Clients vendeur 2 ---")
v2_c = create_clients_and_cultures(v2_clients, vendeurs['vendeur2'])

print("\n--- Clients vendeur 3 ---")
v3_c = create_clients_and_cultures(v3_clients, vendeurs['vendeur3'])

# === COMMANDES LIVRÉES ===
print("\n--- Commandes ---")
produits = {p.code: p for p in Produit.objects.all()}
magasin = User.objects.get(username='magasin1')

def creer_commande(client, vendeur, jours_avant, lignes_data, statut='livree'):
    cmd = Commande.objects.create(
        client=client, vendeur=vendeur, statut=statut,
        preparateur=magasin if statut != 'nouvelle' else None,
    )
    # Fix date
    cmd.date_commande = timezone.now() - timedelta(days=jours_avant)
    Commande.objects.filter(pk=cmd.pk).update(date_commande=cmd.date_commande)

    for code, qty in lignes_data:
        p = produits[code]
        LigneCommande.objects.create(
            commande=cmd, produit=p, quantite=qty,
            prix_unitaire=p.prix_unitaire,
        )

    # Auto facture si livrée
    if statut == 'livree':
        Facture.objects.create(
            commande=cmd,
            statut='payee' if jours_avant > 30 else 'envoyee',
            date_echeance=date.today() + timedelta(days=30 - jours_avant),
            date_paiement=date.today() - timedelta(days=5) if jours_avant > 30 else None,
        )

    print(f"  CMD-{cmd.pk:05d} {client.nom_ferme} ({statut}) - {len(lignes_data)} produits")
    return cmd

# Commandes vendeur 2 - Sophie Bouchard (grosse vendeuse)
creer_commande(v2_c[0], vendeurs['vendeur2'], 60, [('SEM-M001', 8), ('HERB-001', 4), ('FONG-002', 2), ('BIO-001', 3)])
creer_commande(v2_c[0], vendeurs['vendeur2'], 30, [('HERB-003', 5), ('ENG-001', 4), ('ADD-001', 2)])
creer_commande(v2_c[1], vendeurs['vendeur2'], 45, [('SEM-M002', 12), ('HERB-001', 6), ('INSECT-001', 2)])
creer_commande(v2_c[1], vendeurs['vendeur2'], 15, [('SEM-B001', 20), ('HERB-004', 3), ('FONG-001', 3)])
creer_commande(v2_c[2], vendeurs['vendeur2'], 50, [('SEM-S001', 10), ('HERB-001', 5), ('HERB-002', 3)])
creer_commande(v2_c[2], vendeurs['vendeur2'], 20, [('FONG-003', 4), ('ENG-002', 6), ('BIO-002', 3)])
creer_commande(v2_c[2], vendeurs['vendeur2'], 5, [('SEM-M003', 6), ('ADD-002', 3)], statut='en_livraison')

# Commandes vendeur 3 - Martin Pelletier
creer_commande(v3_c[0], vendeurs['vendeur3'], 55, [('SEM-M001', 6), ('SEM-S001', 5), ('HERB-001', 3)])
creer_commande(v3_c[0], vendeurs['vendeur3'], 25, [('FONG-002', 2), ('BIO-001', 2), ('ADD-001', 1)])
creer_commande(v3_c[0], vendeurs['vendeur3'], 10, [('SEM-B002', 10), ('HERB-004', 2)])
creer_commande(v3_c[1], vendeurs['vendeur3'], 40, [('SEM-S003', 12), ('HERB-001', 6), ('HERB-002', 4)])
creer_commande(v3_c[1], vendeurs['vendeur3'], 8, [('FONG-003', 5), ('ENG-002', 4), ('ENG-003', 3), ('BIO-002', 2)])
creer_commande(v3_c[1], vendeurs['vendeur3'], 2, [('SEM-M001', 4)], statut='nouvelle')

# Quelques commandes en plus pour vendeur 1 (Jean Tremblay) - déjà existant
v1_clients = list(Client.objects.filter(vendeur=vendeurs['vendeur1']))
if v1_clients:
    creer_commande(v1_clients[0], vendeurs['vendeur1'], 35, [('HERB-001', 3), ('BIO-002', 2), ('ADD-003', 1)])
    creer_commande(v1_clients[1] if len(v1_clients) > 1 else v1_clients[0], vendeurs['vendeur1'], 12,
                   [('SEM-S002', 8), ('FONG-003', 3), ('ENG-002', 5)])

print(f"\n=== Résumé ===")
print(f"  Vendeurs: {User.objects.filter(role='vendeur').count()}")
print(f"  Clients: {Client.objects.count()}")
print(f"  Commandes: {Commande.objects.count()}")
print(f"  Factures: {Facture.objects.count()}")

for v in User.objects.filter(role='vendeur'):
    cmds = v.commandes_vendeur.filter(statut='livree')
    from decimal import Decimal
    ca = sum((c.total for c in cmds), Decimal('0'))
    print(f"  {v.get_full_name():20s}: {v.clients_assignes.count()} clients, {cmds.count()} livrées, CA={ca}")
