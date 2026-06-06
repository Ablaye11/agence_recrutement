from django import forms
from .models import Candidat, Client, Placement, ClientRequest

class CandidatForm(forms.ModelForm):
    class Meta:
        model = Candidat
        fields = ['photo', 'piece_identite', 'certificat_residence', 'nom', 'prenom', 'age', 'telephone', 'adresse', 'poste_recherche', 'experience', 'disponibilite', 'statut', 'commentaire', 'observations']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'piece_identite': forms.FileInput(attrs={'class': 'form-control'}),
            'certificat_residence': forms.FileInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de famille', 'required': 'required'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénoms', 'required': 'required'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 77 000 00 00', 'required': 'required'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quartier, Ville', 'required': 'required'}),
            'poste_recherche': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'disponibilite': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Commentaire du candidat'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observations internes (Admin)'}),
        }

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'telephone', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet du client', 'required': 'required'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
        }

class PlacementForm(forms.ModelForm):
    class Meta:
        model = Placement
        fields = ['candidat', 'client', 'lieu_travail', 'salaire', 'commission', 'date_debut', 'statut_emploi', 'est_paye', 'date_paiement']
        widgets = {
            'candidat': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'client': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'lieu_travail': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'salaire': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'}),
            'commission': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'required'}),
            'date_paiement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut_emploi': forms.Select(attrs={'class': 'form-control'}),
        }

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Candidat
        fields = ['photo', 'piece_identite', 'certificat_residence', 'nom', 'prenom', 'age', 'telephone', 'adresse', 'poste_recherche', 'experience', 'disponibilite', 'commentaire']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'piece_identite': forms.FileInput(attrs={'class': 'form-control'}),
            'certificat_residence': forms.FileInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom', 'required': 'required'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom', 'required': 'required'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 77 000 00 00', 'required': 'required'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quartier, Ville', 'required': 'required'}),
            'poste_recherche': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Détaillez vos expériences'}),
            'disponibilite': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Avez-vous quelque chose à ajouter ?'}),
        }

class ClientRequestForm(forms.ModelForm):
    class Meta:
        model = ClientRequest
        fields = ['nom_client', 'telephone', 'email', 'poste_recherche', 'quartier', 'budget_max', 'commentaires']
        widgets = {
            'nom_client': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom complet', 'required': 'required'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 77 000 00 00', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com (optionnel)'}),
            'poste_recherche': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'quartier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quartier du travail', 'required': 'required'}),
            'budget_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant en FCFA', 'required': 'required'}),
            'commentaires': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Détails supplémentaires (ex: horaires, tâches...)'}),
        }

