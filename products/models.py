from django.db import models


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


class Produit(models.Model):
    code = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    categorie = models.ForeignKey(
        CategorieProduit,
        on_delete=models.PROTECT,
        related_name='produits',
    )
    format_produit = models.CharField('Format', max_length=100)
    prix_unitaire = models.DecimalField(
        'Prix unitaire', max_digits=10, decimal_places=2,
        null=True, blank=True,
    )
    en_stock = models.BooleanField('En stock', default=True)
    culture_recommandee = models.CharField(
        'Culture recommandée', max_length=200, blank=True,
        help_text='Ex: maïs, soya, blé (séparés par des virgules)',
    )
    image = models.ImageField(upload_to='produits/', blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.nom} ({self.format_produit})"

    class Meta:
        ordering = ['categorie', 'nom']
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'


class RecommandationProduit(models.Model):
    """Lie un produit à un type de culture pour les recommandations automatiques."""
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='recommandations')
    type_culture = models.CharField(max_length=20)
    priorite = models.IntegerField(default=0, help_text='Plus élevé = recommandé en premier')
    description = models.TextField('Pourquoi recommander', blank=True)

    def __str__(self):
        return f"{self.produit.nom} -> {self.type_culture}"

    class Meta:
        ordering = ['-priorite']
        verbose_name = 'Recommandation'
        verbose_name_plural = 'Recommandations'
