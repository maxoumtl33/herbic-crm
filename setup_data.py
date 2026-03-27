"""
Script pour créer les données initiales: utilisateurs, catégories de produits.
Exécuter avec: python3 manage.py shell < setup_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'herbic_crm.settings')
django.setup()

from accounts.models import User
from products.models import CategorieProduit

# Créer superuser/directeur
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        password='admin123',
        email='admin@herbic.com',
        first_name='Admin',
        last_name='Herbic',
        role='directeur',
    )
    print("Superuser 'admin' créé (mot de passe: admin123)")

# Créer un vendeur test
if not User.objects.filter(username='vendeur1').exists():
    User.objects.create_user(
        username='vendeur1',
        password='vendeur123',
        first_name='Jean',
        last_name='Tremblay',
        role='vendeur',
    )
    print("Vendeur 'vendeur1' créé (mot de passe: vendeur123)")

# Créer un magasin test
if not User.objects.filter(username='magasin1').exists():
    User.objects.create_user(
        username='magasin1',
        password='magasin123',
        first_name='Marie',
        last_name='Gagnon',
        role='magasin',
    )
    print("Magasin 'magasin1' créé (mot de passe: magasin123)")

# Créer un client test
if not User.objects.filter(username='client1').exists():
    User.objects.create_user(
        username='client1',
        password='client123',
        first_name='Pierre',
        last_name='Lavoie',
        role='client',
    )
    print("Client 'client1' créé (mot de passe: client123)")

# Créer les catégories de produits
categories = [
    ('Semences de maïs', 'semence'),
    ('Semences de soya', 'semence'),
    ('Semences de blé', 'semence'),
    ('Semences de canola', 'semence'),
    ('Herbicides', 'pesticide'),
    ('Insecticides', 'pesticide'),
    ('Fongicides', 'pesticide'),
    ('Engrais foliaires', 'engrais_foliaire'),
    ('Biostimulants', 'biostimulant'),
    ('Additifs de pulvérisation', 'additif_pulverisation'),
]

for nom, type_cat in categories:
    obj, created = CategorieProduit.objects.get_or_create(
        nom=nom, type_categorie=type_cat
    )
    if created:
        print(f"Catégorie '{nom}' créée")

print("\nConfiguration initiale terminée!")
print("Lancez le serveur avec: python3 manage.py runserver")
print("Accédez à: http://127.0.0.1:8000/")
