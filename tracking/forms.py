from django import forms
from .models import SuiviPousse, StatistiqueCulture


class SuiviPousseForm(forms.ModelForm):
    class Meta:
        model = SuiviPousse
        fields = [
            'date_observation', 'stade_croissance', 'hauteur_cm',
            'densite_plants', 'etat_general', 'problemes_observes',
            'photo', 'notes',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['date_observation'].widget = forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date'}
        )


class StatistiqueCultureForm(forms.ModelForm):
    class Meta:
        model = StatistiqueCulture
        fields = [
            'rendement_estime', 'rendement_reel', 'taux_germination',
            'cout_total_intrants', 'date_semis', 'date_recolte', 'notes',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['date_semis'].widget = forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date'}
        )
        self.fields['date_recolte'].widget = forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date'}
        )
