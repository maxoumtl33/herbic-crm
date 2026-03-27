from django.db import models
from django.conf import settings


class Commande(models.Model):
    class Statut(models.TextChoices):
        NOUVELLE = 'nouvelle', 'Nouvelle'
        EN_PREPARATION = 'en_preparation', 'En préparation'
        PRETE = 'prete', 'Prête'
        EN_LIVRAISON = 'en_livraison', 'En livraison'
        LIVREE = 'livree', 'Livrée'
        ANNULEE = 'annulee', 'Annulée'

    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='commandes',
    )
    vendeur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='commandes_vendeur',
        limit_choices_to={'role': 'vendeur'},
    )
    preparateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='commandes_preparees',
        limit_choices_to={'role__in': ['magasin', 'directeur']},
    )
    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.NOUVELLE,
    )
    notes = models.TextField(blank=True)
    date_commande = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_livraison_prevue = models.DateField('Date de livraison prévue', null=True, blank=True)

    @property
    def total(self):
        return sum(
            ligne.sous_total for ligne in self.lignes.all()
            if ligne.sous_total is not None
        )

    @property
    def nb_lignes(self):
        return self.lignes.count()

    @property
    def nb_lignes_preparees(self):
        return self.lignes.filter(prepare=True).count()

    @property
    def tout_prepare(self):
        return self.nb_lignes > 0 and self.nb_lignes == self.nb_lignes_preparees

    @property
    def progression_preparation(self):
        total = self.nb_lignes
        if total == 0:
            return 0
        return int((self.nb_lignes_preparees / total) * 100)

    def __str__(self):
        return f"CMD-{self.pk:05d} - {self.client.nom_ferme} ({self.get_statut_display()})"

    class Meta:
        ordering = ['-date_commande']
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'


class LigneCommande(models.Model):
    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name='lignes',
    )
    produit = models.ForeignKey(
        'products.Produit',
        on_delete=models.PROTECT,
        related_name='lignes_commande',
    )
    quantite = models.DecimalField(max_digits=10, decimal_places=2)
    prix_unitaire = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
    )
    prepare = models.BooleanField('Préparé', default=False)
    prepare_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='lignes_preparees',
    )
    date_preparation = models.DateTimeField(null=True, blank=True)

    @property
    def sous_total(self):
        if self.prix_unitaire:
            return self.quantite * self.prix_unitaire
        return None

    def __str__(self):
        return f"{self.produit.nom} x {self.quantite}"

    class Meta:
        verbose_name = 'Ligne de commande'
        verbose_name_plural = 'Lignes de commande'
