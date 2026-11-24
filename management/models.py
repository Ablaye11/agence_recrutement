from django.db import models
from datetime import date
import random
import string

class Candidat(models.Model):
    POSTE_CHOICES = [
        ('MENAGE', 'Femme de ménage'),
        ('NOUNOU', 'Nounou garde enfant'),
        ('CUISINE_PRO', 'Cuisinière professionnel'),
        ('CUISINE_SEN', 'Cuisinière plat sénégalais'),
        ('BOY', 'Boy domestique'),
        ('NET_BUREAU', 'Nettoyage bureau'),
        ('NET_3J', 'Nettoyage 3 jour dans la semaine'),
        ('NET_ESCALIER', 'Nettoyage escalier'),
        ('NET_APPART', 'Nettoyage appartement'),
        ('NET_CHANTIER', 'Nettoyage fin de chantier'),
        ('NET_SOIR', 'Nettoyage soir'),
        ('NET_RESTO', 'Nettoyage restaurant'),
        ('VENDEUSE', 'Vendeuse Boutique'),
        ('CAISSIER', 'Caissière (er)'),
        ('SERVEUR', 'Serveuse (er)'),
        ('CHAUFFEUR_P', 'Chauffeur particulier'),
        ('CHAUFFEUR_Y', 'Chauffeur yango'),
        ('LIVREUR_MOTO', 'Chauffeur livreur moto'),
        ('GARDIEN', 'Gardiennage jour ou nuit'),
        ('AIDE_VIE', 'Aide personne âgée'),
        ('GOUVERNANTE', 'Gouvernante'),
        ('CUISINE_NET', 'Cuisine et nettoyage appartement'),
        ('JARDINIER', 'Jardinier'),
        ('SECRETAIRE', 'Secrétaire'),
        ('ASSISTANTE', 'Assistante'),
        ('PLONGE', 'Plongé Restaurant'),
        ('LINGERE', 'Lingère et repassage'),
        ('CUISINE_NETTOYAGE', 'Cuisine et nettoyage'),
        ('NOUNOU_NETTOYAGE', 'Nounou et nettoyage'),
        ('CUISINE_NOUNOU', 'Cuisine et nounou'),
        ('NETTOYAGE_SIMPLE', 'Nettoyage'),
        ('SOCIETE_DE_NETTOYAGE_DAKAR_TERMINUS', 'Societe de nettoyage Dakar Terminus'),
        ('AUTRE', 'Autre.....'),
    ]

    DISPO_CHOICES = [
        ('JOURNALIER', 'Journalier'),
        ('DAILY', 'Descend chaque jour'),
        ('WEEKLY', 'Descente chaque semaine'),
        ('BI_WEEKLY', 'Descend chaque 15 jours'),
        ('LIVE_IN', 'Logée'),
        ('LIVE_OUT', 'Non logée'),
    ]

    STATUT_CHOICES = [
        ('AVAILABLE', 'Disponible'),
        ('PLACED', 'Placé'),
        ('WAITING', 'En attente'),
        ('REFUSED', 'Refusé'),
        ('PAYMENT_PENDING', 'En attente de paiement'),
    ]

    matricule = models.CharField(max_length=20, unique=True, editable=False)
    photo = models.ImageField(upload_to='candidats/', blank=True, null=True)
    piece_identite = models.FileField(upload_to='documents/cni/', verbose_name="Carte d'Identité Recto (PDF/Image)", blank=True, null=True)
    piece_identite_verso = models.FileField(upload_to='documents/cni/', null=True, blank=True, verbose_name="Carte d'Identité Verso")
    certificat_residence = models.FileField(upload_to='documents/residence/', null=True, blank=True, verbose_name="Certificat de Résidence")
    nom = models.CharField(max_length=100, blank=True, default='')
    prenom = models.CharField(max_length=100, blank=True, default='')
    age = models.PositiveIntegerField(null=True, blank=True, default=25)
    telephone = models.CharField(max_length=20)
    adresse = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True, verbose_name="Email (facultatif)")
    tuteur = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tuteur (Nom et Téléphone)")
    poste_recherche = models.CharField(max_length=50, choices=POSTE_CHOICES, db_index=True)
    experience = models.TextField(blank=True, default='')
    disponibilite = models.CharField(max_length=50, choices=DISPO_CHOICES, default='JOURNALIER')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='AVAILABLE', db_index=True)
    frais_paye = models.BooleanField(default=False, verbose_name="Frais de dossier payés")
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID Transaction Paiement")
    commentaire = models.TextField(blank=True, null=True, verbose_name="Commentaire (Candidat)")
    observations = models.TextField(blank=True, verbose_name="Observations (Admin)")
    date_inscription = models.DateTimeField(auto_now_add=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.matricule:
            # Génération d'un matricule unique type CAND-XXXX
            while True:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                new_matricule = f"CAND-{code}"
                if not Candidat.objects.filter(matricule=new_matricule).exists():
                    self.matricule = new_matricule
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenom}"

    class Meta:
        verbose_name = "Candidat"
        verbose_name_plural = "Candidats"

class Client(models.Model):
    nom = models.CharField(max_length=200)
    telephone = models.CharField(max_length=20)
    adresse = models.CharField(max_length=255)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

class Placement(models.Model):
    STATUT_EMPLOI = [
        ('ACTIVE', 'En poste'),
        ('TERMINATED', 'Contrat terminé'),
        ('LEFT', 'A quitté le poste'),
    ]

    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE, related_name='placements')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='placements')
    lieu_travail = models.CharField(max_length=255)
    salaire = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Frais de l'agence")
    date_debut = models.DateField()
    statut_emploi = models.CharField(max_length=20, choices=STATUT_EMPLOI, default='ACTIVE')
    est_paye = models.BooleanField(default=False, verbose_name="Frais payés")
    date_paiement = models.DateField(null=True, blank=True, verbose_name="Date de réception du paiement")
    date_fin = models.DateField(null=True, blank=True, verbose_name="Date de fin de contrat")
    date_placement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Placement de {self.candidat} chez {self.client}"

    class Meta:
        verbose_name = "Placement"
        verbose_name_plural = "Placements"

class Notification(models.Model):
    TYPES = [
        ('INFO', 'Information'),
        ('SUCCESS', 'Succès'),
        ('WARNING', 'Alerte'),
        ('DANGER', 'Urgent'),
    ]
    titre = models.CharField(max_length=200)
    message = models.TextField()
    type_notif = models.CharField(max_length=10, choices=TYPES, default='INFO')
    lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return self.titre

class Expense(models.Model):
    CATEGORIES = [
        ('LOYER', 'Loyer'),
        ('SALAIRE', 'Salaires Staff'),
        ('INTERNET', 'Internet & Tel'),
        ('MARKETING', 'Publicité'),
        ('AUTRE', 'Autre'),
    ]
    titre = models.CharField(max_length=200)
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_depense = models.DateField(default=date.today)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_depense']
        verbose_name = "Dépense"
        verbose_name_plural = "Dépenses"

    def __str__(self):
        return f"{self.titre} - {self.montant} FCFA"

class ClientRequest(models.Model):
    nom_client = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    poste_recherche = models.CharField(max_length=50, choices=Candidat.POSTE_CHOICES)
    quartier = models.CharField(max_length=100)
    budget_max = models.DecimalField(max_digits=10, decimal_places=0, help_text="Budget mensuel (FCFA)")
    commentaires = models.TextField(blank=True, null=True)
    date_demande = models.DateTimeField(auto_now_add=True)
    STATUT_CHOICES = [
        ('PENDING', 'En attente'),
        ('ACCEPTED', 'Acceptée'),
        ('REFUSED', 'Refusée'),
    ]
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='PENDING')

    def __str__(self):
        return f"Demande de {self.nom_client} - {self.get_poste_recherche_display()}"

    class Meta:
        ordering = ['-date_demande']


class PreInscription(models.Model):
    """
    Sas d'inscription temporaire : les données des candidats qui s'inscrivent en ligne
    sont stockées ici UNIQUEMENT. Elles ne sont transférées dans la table Candidat
    qu'une fois le paiement PayTech validé avec succès.
    """
    ref_command = models.CharField(max_length=100, unique=True, db_index=True)
    poste_recherche = models.CharField(max_length=50, choices=Candidat.POSTE_CHOICES)
    telephone = models.CharField(max_length=30)
    adresse = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True, verbose_name="Email (facultatif)")
    tuteur = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nom et Téléphone du Tuteur")
    nom = models.CharField(max_length=100, blank=True, default='')
    prenom = models.CharField(max_length=100, blank=True, default='')
    age = models.PositiveIntegerField(null=True, blank=True)
    experience = models.TextField(blank=True, default='')
    disponibilite = models.CharField(max_length=50, choices=Candidat.DISPO_CHOICES, default='JOURNALIER')
    photo = models.ImageField(upload_to='temp_inscriptions/photos/', blank=True, null=True)
    piece_identite = models.FileField(upload_to='temp_inscriptions/cni/', blank=True, null=True, verbose_name="CNI Recto")
    piece_identite_verso = models.FileField(upload_to='temp_inscriptions/cni/', blank=True, null=True, verbose_name="CNI Verso")
    montant = models.IntegerField(default=5000, verbose_name="Montant frais (FCFA)")
    statut_paiement = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'En attente de paiement'),
            ('PAID', 'Payé'),
            ('FAILED', 'Échoué/Annulé'),
        ],
        default='PENDING',
        db_index=True
    )
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID Transaction PayTech")
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pré-inscription {self.ref_command} - {self.telephone} ({self.poste_recherche}) - {self.statut_paiement}"

    def transfer_to_candidat(self, transaction_token=None):
        """
        Transfère la pré-inscription vers la table Candidat après validation du paiement.
        Garantit que la table Candidat n'est jamais polluée tant que le paiement n'est pas effectué.
        """
        token = transaction_token or self.transaction_id or self.ref_command

        # Éviter les doublons
        existant = Candidat.objects.filter(transaction_id=token).first()
        if existant:
            self.statut_paiement = 'PAID'
            self.save(update_fields=['statut_paiement'])
            return existant

        nom_val = self.nom.strip() if self.nom else "Candidat"
        prenom_val = self.prenom.strip() if self.prenom else self.telephone

        candidat = Candidat(
            nom=nom_val,
            prenom=prenom_val,
            age=self.age if self.age else 25,
            telephone=self.telephone,
            adresse=self.adresse,
            email=self.email,
            tuteur=self.tuteur,
            poste_recherche=self.poste_recherche,
            experience=self.experience,
            disponibilite=self.disponibilite,
            statut='WAITING',  # Reçu et payé, en attente d'approbation administrative
            frais_paye=True,
            transaction_id=token,
            commentaire=f"Inscription en ligne payée. Tuteur: {self.tuteur or 'Non spécifié'}."
        )

        if self.photo:
            candidat.photo = self.photo
        if self.piece_identite:
            candidat.piece_identite = self.piece_identite
        if self.piece_identite_verso:
            candidat.piece_identite_verso = self.piece_identite_verso

        candidat.save()

        self.statut_paiement = 'PAID'
        if transaction_token:
            self.transaction_id = transaction_token
        self.save()

        return candidat

    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Pré-inscription en attente de paiement"
        verbose_name_plural = "Pré-inscriptions en attente de paiement"

