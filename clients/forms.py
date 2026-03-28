from django import forms
from .models import Client, Culture, ProduitArrosage, TypeCulture


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'code', 'nom_ferme', 'prenom', 'nom', 'adresse', 'ville',
            'code_postal', 'telephone', 'cellulaire', 'courriel',
            'vendeur', 'notes',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['notes'].widget.attrs['rows'] = 3


class CultureForm(forms.ModelForm):
    class Meta:
        model = Culture
        fields = [
            'type_culture', 'nom_champ', 'superficie_acres', 'semence',
            'population_visee', 'population_reelle', 'annee', 'notes',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['notes'].widget.attrs['rows'] = 2


class ProduitArrosageForm(forms.ModelForm):
    class Meta:
        model = ProduitArrosage
        fields = ['nom_produit', 'dose', 'quantite_totale', 'unite', 'date_application', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['date_application'].widget = forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date'}
        )


class TypeCultureForm(forms.ModelForm):
    class Meta:
        model = TypeCulture
        fields = ['code', 'nom']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ClientSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par nom, ferme, code...',
        })
    )
