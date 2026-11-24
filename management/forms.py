from django import forms
from .models import Candidat, Client, Placement, ClientRequest, PreInscription

class CandidatForm(forms.ModelForm):
    class Meta:
        model = Candidat
        fields = ['photo', 'piece_identite', 'piece_identite_verso', 'certificat_residence', 'nom', 'prenom', 'age', 'telephone', 'adresse', 'tuteur', 'poste_recherche', 'experience', 'disponibilite', 'statut', 'commentaire', 'observations']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'piece_identite': forms.FileInput(attrs={'class': 'form-control'}),
            'piece_identite_verso': forms.FileInput(attrs={'class': 'form-control'}),
            'certificat_residence': forms.FileInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de famille'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénoms'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 77 000 00 00', 'required': 'required'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quartier, Ville', 'required': 'required'}),
            'tuteur': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom et Téléphone du Tuteur'}),
            'poste_recherche': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'disponibilite': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Commentaire du candidat'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observations internes (Admin)'}),
        }

class PreInscriptionForm(forms.ModelForm):
    """Formulaire standard de pré-inscription pour paiement sécurisé"""
    class Meta:
        model = PreInscription
        fields = ['photo', 'piece_identite', 'piece_identite_verso', 'nom', 'prenom', 'age', 'telephone', 'adresse', 'tuteur', 'poste_recherche', 'experience', 'disponibilite']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'piece_identite': forms.FileInput(attrs={'class': 'form-control'}),
            'piece_identite_verso': forms.FileInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 77 000 00 00', 'required': 'required'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quartier, Ville', 'required': 'required'}),
            'tuteur': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom et numéro du tuteur'}),
            'poste_recherche': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Détaillez vos expériences'}),
            'disponibilite': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        }

class SimplifiedPreInscriptionForm(forms.ModelForm):
    """
    Formulaire test accessible pour analphabètes et personnes en apprentissage.
    Requis : Métier (sélection visuelle parmi les 33 de prod), Photo Selfie, CNI Recto, CNI Verso, Téléphone, Adresse, Tuteur, Âge.
    Options complémentaires de prod : Disponibilité, Expérience, Email, Nom, Prénom.
    """
    class Meta:
        model = PreInscription
        fields = ['poste_recherche', 'photo', 'piece_identite', 'piece_identite_verso', 'telephone', 'adresse', 'tuteur', 'age', 'disponibilite', 'experience', 'email', 'nom', 'prenom']
        widgets = {
            'poste_recherche': forms.HiddenInput(), # Rempli par le clic sur la carte visuelle (33 métiers)
            'disponibilite': forms.HiddenInput(), # Rempli par les cartes de disponibilité (Logée, Non logée...)
            'experience': forms.HiddenInput(), # Rempli par le choix visuel d'expérience
            'photo': forms.FileInput(attrs={
                'class': 'visually-hidden-input',
                'accept': 'image/*',
                'capture': 'user' # Active la caméra frontale pour le selfie
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control touch-input',
                'placeholder': 'Ex: 77 123 45 67',
                'required': 'required',
                'type': 'tel',
                'autocomplete': 'tel'
            }),
            'adresse': forms.TextInput(attrs={
                'class': 'form-control touch-input',
                'placeholder': 'Quartier (ex: Grand Yoff, Pikine...)',
                'required': 'required'
            }),
            'tuteur': forms.TextInput(attrs={
                'class': 'form-control touch-input',
                'placeholder': 'Nom et numéro de votre tuteur',
                'required': 'required'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control touch-input',
                'placeholder': 'Ex: 25 ans',
                'min': '18',
                'max': '70',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control touch-input',
                'placeholder': 'votre.email@exemple.com (facultatif)',
                'autocomplete': 'email'
            }),
            'piece_identite': forms.FileInput(attrs={
                'class': 'visually-hidden-input',
                'accept': 'image/*',
                'capture': 'environment'
            }),
            'piece_identite_verso': forms.FileInput(attrs={
                'class': 'visually-hidden-input',
                'accept': 'image/*',
                'capture': 'environment'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control touch-input',
                'placeholder': 'Votre Nom (facultatif si sur la carte)'
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'form-control touch-input',
                'placeholder': 'Votre Prénom (facultatif si sur la carte)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'disponibilite' in self.fields:
            self.fields['disponibilite'].required = False
        if 'experience' in self.fields:
            self.fields['experience'].required = False
        if 'email' in self.fields:
            self.fields['email'].required = False
        if 'nom' in self.fields:
            self.fields['nom'].required = False
        if 'prenom' in self.fields:
            self.fields['prenom'].required = False

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

