from django.db import models
from clients.models import TypeCulture


class CategorieProduit(models.Model):
    class TypeCategorie(models.TextChoices):
        SEMENCE = 'semence', 'Semence'
        PESTICIDE = 'pesticide', 'Pesticide'
        ENGRAIS_FOLIAIRE = 'engrais_foliaire', 'Engrais foliaire'
        BIOSTIMULANT = 'biostimulant', 'Biostimulant'
        ADDITIF_PULVERISATION = 'additif_pulverisation', 'Additif de pulvérisation'

    nom = models.CharField(max_length=100)
    type_categorie = models.CharField(
        max_length=30,
        choices=TypeCategorie.choices,
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = 'Catégorie de produit'
        verbose_name_plural = 'Catégories de produits'


class Unite(models.TextChoices):
    LITRE = 'L', 'Litres (L)'
    MILLILITRE = 'mL', 'Millilitres (mL)'
    KILOGRAMME = 'kg', 'Kilogrammes (kg)'
    LIVRE = 'lb', 'Livres (lb)'
    GRAIN = 'grains', 'Grains'
    UNITE = 'unite', 'Unité'


class TypeContenant(models.TextChoices):
    BIDON = 'bidon', 'Bidon'
    SAC = 'sac', 'Sac'
    BOITE = 'boite', 'Boîte'
    BARIL = 'baril', 'Baril'
    AUTRE = 'autre', 'Autre'


# Table de conversion vers l'unité de base
# L est la base pour les liquides, kg pour les poids, grains pour les semences
CONVERSIONS = {
    ('mL', 'L'): 0.001,
    ('L', 'mL'): 1000,
    ('L', 'L'): 1,
    ('mL', 'mL'): 1,
    ('lb', 'kg'): 0.4536,
    ('kg', 'lb'): 2.2046,
    ('kg', 'kg'): 1,
    ('lb', 'lb'): 1,
    ('grains', 'grains'): 1,
    ('unite', 'unite'): 1,
}


class Produit(models.Model):
    code = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    categorie = models.ForeignKey(
        CategorieProduit,
        on_delete=models.PROTECT,
        related_name='produits',
    )
    # Format affiché (ex: "Bidon 10 L")
    format_produit = models.CharField('Format', max_length=100)
    # Contenance structurée pour le calcul
    contenant = models.CharField(
        'Type de contenant', max_length=20,
        choices=TypeContenant.choices,
        default=TypeContenant.BIDON,
    )
    contenance_valeur = models.DecimalField(
        'Contenance', max_digits=12, decimal_places=2,
        null=True, blank=True,
        help_text='Ex: 10 pour un Bidon 10L, 80000 pour un Sac 80000 grains',
    )
    contenance_unite = models.CharField(
        'Unité de contenance', max_length=10,
        choices=Unite.choices,
        default=Unite.LITRE,
    )

    prix_unitaire = models.DecimalField(
        'Prix unitaire', max_digits=10, decimal_places=2,
        null=True, blank=True,
    )
    en_stock = models.BooleanField('En stock', default=True)
    cultures_recommandees = models.ManyToManyField(
        TypeCulture,
        blank=True,
        related_name='produits_recommandes',
        verbose_name='Cultures recommandées',
    )
    image = models.ImageField(upload_to='produits/', blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    @property
    def label_contenant(self):
        """Retourne 'bidon', 'sac', etc."""
        return self.get_contenant_display()

    def __str__(self):
        return f"{self.code} - {self.nom} ({self.format_produit})"

    class Meta:
        ordering = ['categorie', 'nom']
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'


class RecommandationProduit(models.Model):
    """Lie un produit à un type de culture pour les recommandations automatiques."""

    class Saison(models.TextChoices):
        PRE_SEMIS = 'pre_semis', 'Pré-semis (mars-avril)'
        SEMIS = 'semis', 'Semis (mai)'
        POST_LEVEE = 'post_levee', 'Post-levée (juin)'
        CROISSANCE = 'croissance', 'Croissance (juillet)'
        FLORAISON = 'floraison', 'Floraison (juillet-août)'
        RECOLTE = 'recolte', 'Pré-récolte (sept-oct)'
        TOUTE_SAISON = 'toute_saison', 'Toute la saison'

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='recommandations')
    type_culture = models.ForeignKey(
        TypeCulture,
        on_delete=models.CASCADE,
        related_name='recommandations',
        verbose_name='Type de culture',
        null=True,
    )
    priorite = models.IntegerField(default=0, help_text='Plus élevé = recommandé en premier')
    description = models.TextField('Pourquoi recommander', blank=True)

    # Dose structurée pour le calcul
    dose_valeur = models.DecimalField(
        'Dose par acre (valeur)', max_digits=12, decimal_places=4,
        null=True, blank=True,
        help_text='Ex: 1.67, 315, 80000',
    )
    dose_unite = models.CharField(
        'Unité de dose', max_length=10,
        choices=Unite.choices,
        blank=True, default='',
    )
    dose_affichage = models.CharField(
        'Dose (affichage)', max_length=100, blank=True,
        help_text='Texte affiché: "1.67 L/acre", "1 sac/2 acres"',
    )

    saison = models.CharField(
        max_length=20,
        choices=Saison.choices,
        default=Saison.TOUTE_SAISON,
    )
    complementaire_de = models.ForeignKey(
        Produit, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='produits_complementaires',
        help_text='Si le client achète ce produit, recommander le produit principal',
    )
    probleme_cible = models.CharField(
        'Problème ciblé', max_length=200, blank=True,
        help_text='Ex: chrysomèle, cercospora, mauvaises herbes résistantes',
    )

    def __str__(self):
        return f"{self.produit.nom} -> {self.type_culture}"

    class Meta:
        ordering = ['-priorite']
        verbose_name = 'Recommandation'
        verbose_name_plural = 'Recommandations'
