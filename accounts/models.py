from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = 'client', 'Client'
        VENDEUR = 'vendeur', 'Vendeur'
        MAGASIN = 'magasin', 'Magasin'
        DIRECTEUR = 'directeur', 'Directeur'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
    )
    telephone = models.CharField(max_length=20, blank=True)
    cellulaire = models.CharField(max_length=20, blank=True)

    def is_client(self):
        return self.role == self.Role.CLIENT

    def is_vendeur(self):
        return self.role == self.Role.VENDEUR

    def is_magasin(self):
        return self.role == self.Role.MAGASIN

    def is_directeur(self):
        return self.role == self.Role.DIRECTEUR

    def has_staff_access(self):
        return self.role in (self.Role.VENDEUR, self.Role.MAGASIN, self.Role.DIRECTEUR)

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
