from django import forms
from .models import Produit, CategorieProduit, RecommandationProduit


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = [
            'code', 'nom', 'description', 'categorie', 'format_produit',
            'prix_unitaire', 'en_stock', 'culture_recommandee', 'image',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'en_stock':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'


class CategorieForm(forms.ModelForm):
    class Meta:
        model = CategorieProduit
        fields = ['nom', 'type_categorie', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class RecommandationForm(forms.ModelForm):
    class Meta:
        model = RecommandationProduit
        fields = ['produit', 'type_culture', 'priorite', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
