from django.db import models
from django.conf import settings


class Client(models.Model):
    code = models.CharField(max_length=50, unique=True)
    nom_ferme = models.CharField('Nom de la ferme', max_length=200)
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=300)
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10)
    telephone = models.CharField('No téléphone', max_length=20, blank=True)
    cellulaire = models.CharField('No cellulaire', max_length=20, blank=True)
    courriel = models.EmailField(blank=True)
    notes = models.TextField(blank=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='client_profile',
    )
    vendeur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='clients_assignes',
        limit_choices_to={'role': 'vendeur'},
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.nom_ferme} ({self.prenom} {self.nom})"

    class Meta:
        ordering = ['nom_ferme']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'


class Culture(models.Model):
    class TypeCulture(models.TextChoices):
        MAIS = 'mais', 'Maïs'
        SOYA = 'soya', 'Soya'
        BLE = 'ble', 'Blé'
        ORGE = 'orge', 'Orge'
        AVOINE = 'avoine', 'Avoine'
        CANOLA = 'canola', 'Canola'
        FOIN = 'foin', 'Foin'
        AUTRE = 'autre', 'Autre'

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='cultures')
    type_culture = models.CharField(max_length=20, choices=TypeCulture.choices)
    nom_champ = models.CharField('Nom du champ', max_length=100, blank=True)
    superficie_acres = models.DecimalField('Superficie (acres)', max_digits=10, decimal_places=2)
    semence = models.CharField('Semence utilisée', max_length=200, blank=True)
    population_visee = models.IntegerField('Population visée (grains/acre)', null=True, blank=True)
    population_reelle = models.IntegerField('Population réelle (grains/acre)', null=True, blank=True)
    annee = models.IntegerField('Année')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.client.nom_ferme} - {self.get_type_culture_display()} ({self.annee})"

    class Meta:
        ordering = ['-annee', 'type_culture']
        verbose_name = 'Culture'
        verbose_name_plural = 'Cultures'


class ProduitArrosage(models.Model):
    culture = models.ForeignKey(Culture, on_delete=models.CASCADE, related_name='produits_arrosage')
    nom_produit = models.CharField(max_length=200)
    dose = models.CharField('Dose par acre', max_length=100)
    quantite_totale = models.DecimalField('Quantité totale', max_digits=10, decimal_places=2)
    unite = models.CharField(max_length=20, default='L')
    date_application = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nom_produit} - {self.dose}/acre"

    class Meta:
        verbose_name = "Produit d'arrosage"
        verbose_name_plural = "Produits d'arrosage"
