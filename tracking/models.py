from django.db import models
from django.conf import settings


class JournalActivite(models.Model):
    """Journal d'audit pour tracer toutes les actions importantes."""
    class TypeAction(models.TextChoices):
        CREATION = 'creation', 'Création'
        MODIFICATION = 'modification', 'Modification'
        SUPPRESSION = 'suppression', 'Suppression'
        STATUT = 'statut', 'Changement de statut'
        STOCK = 'stock', 'Mise à jour stock'
        CONNEXION = 'connexion', 'Connexion'

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    action = models.CharField(max_length=20, choices=TypeAction.choices)
    entite = models.CharField(max_length=50, help_text='Ex: Commande, Client, Produit')
    entite_id = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date:%d/%m %H:%M} - {self.utilisateur} - {self.description}"

    class Meta:
        ordering = ['-date']
        verbose_name = "Journal d'activité"
        verbose_name_plural = "Journal d'activité"


def log_action(user, action, entite, entite_id, description):
    """Helper pour créer une entrée de journal."""
    JournalActivite.objects.create(
        utilisateur=user,
        action=action,
        entite=entite,
        entite_id=entite_id,
        description=description,
    )


class SuiviPousse(models.Model):
    culture = models.ForeignKey(
        'clients.Culture',
        on_delete=models.CASCADE,
        related_name='suivis_pousse',
    )
    date_observation = models.DateField()
    stade_croissance = models.CharField('Stade de croissance', max_length=100)
    hauteur_cm = models.DecimalField(
        'Hauteur (cm)', max_digits=6, decimal_places=1,
        null=True, blank=True,
    )
    densite_plants = models.IntegerField(
        'Densité de plants (plants/acre)',
        null=True, blank=True,
    )
    etat_general = models.CharField(
        'État général',
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('bon', 'Bon'),
            ('moyen', 'Moyen'),
            ('faible', 'Faible'),
            ('mauvais', 'Mauvais'),
        ],
        default='bon',
    )
    problemes_observes = models.TextField('Problèmes observés', blank=True)
    photo = models.ImageField(upload_to='suivis/', blank=True)
    notes = models.TextField(blank=True)

    observateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.culture} - {self.date_observation} ({self.get_etat_general_display()})"

    class Meta:
        ordering = ['-date_observation']
        verbose_name = 'Suivi de pousse'
        verbose_name_plural = 'Suivis de pousse'


class StatistiqueCulture(models.Model):
    culture = models.OneToOneField(
        'clients.Culture',
        on_delete=models.CASCADE,
        related_name='statistiques',
    )
    rendement_estime = models.DecimalField(
        'Rendement estimé (boiss./acre)',
        max_digits=8, decimal_places=2,
        null=True, blank=True,
    )
    rendement_reel = models.DecimalField(
        'Rendement réel (boiss./acre)',
        max_digits=8, decimal_places=2,
        null=True, blank=True,
    )
    taux_germination = models.DecimalField(
        'Taux de germination (%)',
        max_digits=5, decimal_places=2,
        null=True, blank=True,
    )
    cout_total_intrants = models.DecimalField(
        'Coût total intrants ($)',
        max_digits=10, decimal_places=2,
        null=True, blank=True,
    )
    date_semis = models.DateField('Date de semis', null=True, blank=True)
    date_recolte = models.DateField('Date de récolte', null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Stats - {self.culture}"

    class Meta:
        verbose_name = 'Statistique de culture'
        verbose_name_plural = 'Statistiques de culture'
