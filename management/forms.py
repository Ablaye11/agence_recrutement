from django import forms
from .models import Candidat, Client, Placement

class CandidatForm(forms.ModelForm):
    class Meta:
        model = Candidat
        fields = ['photo', 'piece_identite', 'nom', 'prenom', 'age', 'telephone', 'adresse', 'poste_recherche', 'experience', 'disponibilite', 'statut', 'observations']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de famille'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénoms'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 77 000 00 00'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quartier, Ville'}),
            'poste_recherche': forms.Select(attrs={'class': 'form-control'}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'disponibilite': forms.Select(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'telephone', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet du client'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PlacementForm(forms.ModelForm):
    class Meta:
        model = Placement
        fields = ['candidat', 'client', 'lieu_travail', 'salaire', 'commission', 'date_debut', 'statut_emploi', 'est_paye', 'date_paiement']
        widgets = {
            'candidat': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'lieu_travail': forms.TextInput(attrs={'class': 'form-control'}),
            'salaire': forms.NumberInput(attrs={'class': 'form-control'}),
            'commission': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_paiement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut_emploi': forms.Select(attrs={'class': 'form-control'}),
        }
