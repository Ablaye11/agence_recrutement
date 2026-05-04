from django import forms
from .models import Candidat, Client, Placement, ClientRequest

class CandidatForm(forms.ModelForm):
    class Meta:
        model = Candidat
        fields = ['photo', 'piece_identite', 'certificat_medical', 'nom', 'prenom', 'age', 'telephone', 'adresse', 'poste_recherche', 'experience', 'disponibilite', 'statut', 'observations']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'piece_identite': forms.FileInput(attrs={'class': 'form-control'}),
            'certificat_medical': forms.FileInput(attrs={'class': 'form-control'}),
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

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Candidat
        fields = ['nom', 'prenom', 'age', 'telephone', 'adresse', 'poste_recherche', 'experience', 'disponibilite']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'poste_recherche': forms.Select(attrs={'class': 'form-control'}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'disponibilite': forms.Select(attrs={'class': 'form-control'}),
        }

class ClientRequestForm(forms.ModelForm):
    class Meta:
        model = ClientRequest
        fields = ['nom_client', 'telephone', 'email', 'poste_recherche', 'quartier', 'budget_max', 'commentaires']
        widgets = {
            'nom_client': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom complet'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 77 000 00 00'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com (optionnel)'}),
            'poste_recherche': forms.Select(attrs={'class': 'form-control'}),
            'quartier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quartier du travail'}),
            'budget_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant en FCFA'}),
            'commentaires': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Détails supplémentaires (ex: horaires, tâches...)'}),
        }
