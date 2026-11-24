from django.contrib import admin
from .models import Candidat, Client, Placement, PreInscription, Notification, Expense, ClientRequest

admin.site.site_header = "Administration DAKAR TERMINUS"
admin.site.site_title = "DAKAR TERMINUS"
admin.site.index_title = "Gestion de l'Agence"

from django.utils.html import format_html

@admin.register(PreInscription)
class PreInscriptionAdmin(admin.ModelAdmin):
    list_display = ('ref_command', 'nom', 'prenom', 'poste_recherche', 'telephone', 'tuteur', 'statut_paiement', 'date_creation')
    list_filter = ('statut_paiement', 'poste_recherche', 'date_creation')
    search_fields = ('ref_command', 'nom', 'prenom', 'telephone', 'tuteur')
    readonly_fields = ('ref_command', 'date_creation')

@admin.register(Candidat)
class CandidatAdmin(admin.ModelAdmin):
    def photo_tag(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />', obj.photo.url)
        return "-"
    photo_tag.short_description = 'Photo'

    list_display = ('photo_tag', 'matricule', 'nom', 'prenom', 'poste_recherche', 'statut', 'frais_paye', 'date_inscription')
    list_filter = ('statut', 'frais_paye', 'poste_recherche', 'disponibilite')
    search_fields = ('matricule', 'nom', 'prenom', 'telephone', 'tuteur')
    readonly_fields = ('matricule', 'date_inscription')
    fieldsets = (
        ('Identification', {
            'fields': ('matricule', 'photo', 'piece_identite', 'piece_identite_verso', 'nom', 'prenom', 'age')
        }),
        ('Coordonnées & Garant', {
            'fields': ('telephone', 'adresse', 'tuteur')
        }),
        ('Profil Professionnel', {
            'fields': ('poste_recherche', 'experience', 'disponibilite', 'statut', 'frais_paye', 'transaction_id')
        }),
        ('Notes', {
            'fields': ('commentaire', 'observations', 'date_inscription')
        }),
    )

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone', 'adresse')
    search_fields = ('nom', 'telephone')

@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    list_display = ('candidat', 'client', 'salaire', 'date_debut', 'statut_emploi', 'est_paye')
    list_filter = ('statut_emploi', 'est_paye', 'date_debut')
    search_fields = ('candidat__nom', 'candidat__prenom', 'client__nom')
    list_editable = ('est_paye', 'statut_emploi')
