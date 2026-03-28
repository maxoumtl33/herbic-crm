from django.db import models
from django.conf import settings


class Commande(models.Model):
    class Statut(models.TextChoices):
        VERIFICATION = 'verification', 'En vérification'
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
    creee_par_client = models.BooleanField('Créée par le client', default=False)
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


class Facture(models.Model):
    class StatutFacture(models.TextChoices):
        BROUILLON = 'brouillon', 'Brouillon'
        ENVOYEE = 'envoyee', 'Envoyée'
        PAYEE = 'payee', 'Payée'
        EN_RETARD = 'en_retard', 'En retard'
        ANNULEE = 'annulee', 'Annulée'

    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE,
        related_name='facture',
    )
    numero = models.CharField(max_length=20, unique=True, blank=True)
    statut = models.CharField(
        max_length=20,
        choices=StatutFacture.choices,
        default=StatutFacture.BROUILLON,
    )
    date_emission = models.DateField(auto_now_add=True)
    date_echeance = models.DateField('Date d\'échéance', null=True, blank=True)
    date_paiement = models.DateField('Date de paiement', null=True, blank=True)
    notes = models.TextField(blank=True)

    TAUX_TPS = 5.0
    TAUX_TVQ = 9.975

    @property
    def sous_total_ht(self):
        return self.commande.total or 0

    @property
    def montant_tps(self):
        from decimal import Decimal
        return (Decimal(str(self.sous_total_ht)) * Decimal('0.05')).quantize(Decimal('0.01'))

    @property
    def montant_tvq(self):
        from decimal import Decimal
        return (Decimal(str(self.sous_total_ht)) * Decimal('0.09975')).quantize(Decimal('0.01'))

    @property
    def total_ttc(self):
        from decimal import Decimal
        ht = Decimal(str(self.sous_total_ht))
        return (ht + self.montant_tps + self.montant_tvq).quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        if not self.numero:
            super().save(*args, **kwargs)
            self.numero = f'FAC-{self.pk:05d}'
            super().save(update_fields=['numero'])
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero} - {self.commande.client.nom_ferme}"

    class Meta:
        ordering = ['-date_emission']
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'


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
