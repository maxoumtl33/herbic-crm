from django import forms
from .models import Commande, LigneCommande


class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['client', 'notes', 'date_livraison_prevue']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['date_livraison_prevue'].widget = forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date'}
        )
        self.fields['notes'].widget.attrs['rows'] = 3


class LigneCommandeForm(forms.ModelForm):
    class Meta:
        model = LigneCommande
        fields = ['produit', 'quantite', 'prix_unitaire']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


LigneCommandeFormSet = forms.inlineformset_factory(
    Commande, LigneCommande,
    form=LigneCommandeForm,
    extra=3,
    can_delete=True,
)


class CommandeStatutForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['statut']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['statut'].widget.attrs['class'] = 'form-select'
