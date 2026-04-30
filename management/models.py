from django.db import models
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
        ('AUTRE', 'Autre.....'),
    ]

    DISPO_CHOICES = [
        ('DAILY', 'Tous les jours'),
        ('BI_WEEKLY', 'Descend chaque 15 jours'),
        ('LIVE_IN', 'Logée'),
        ('LIVE_OUT', 'Non logée'),
    ]

    STATUT_CHOICES = [
        ('AVAILABLE', 'Disponible'),
        ('PLACED', 'Placé'),
        ('WAITING', 'En attente'),
    ]

    matricule = models.CharField(max_length=20, unique=True, editable=False)
    photo = models.ImageField(upload_to='candidats/', null=True, blank=True)
    piece_identite = models.FileField(upload_to='documents/cni/', null=True, blank=True, verbose_name="Carte d'Identité (PDF/Image)")
    certificat_medical = models.FileField(upload_to='documents/sante/', null=True, blank=True, verbose_name="Certificat Médical")
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    telephone = models.CharField(max_length=20)
    adresse = models.CharField(max_length=255)
    poste_recherche = models.CharField(max_length=50, choices=POSTE_CHOICES)
    experience = models.TextField()
    disponibilite = models.CharField(max_length=50, choices=DISPO_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='AVAILABLE')
    observations = models.TextField(blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)

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
