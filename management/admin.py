from django.contrib import admin
from .models import Candidat, Client, Placement

admin.site.site_header = "Administration AGENCE PRO"
admin.site.site_title = "AGENCE PRO"
admin.site.index_title = "Gestion de l'Agence"

from django.utils.html import format_html

@admin.register(Candidat)
class CandidatAdmin(admin.ModelAdmin):
    def photo_tag(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />', obj.photo.url)
        return "-"
    photo_tag.short_description = 'Photo'

    list_display = ('photo_tag', 'matricule', 'nom', 'prenom', 'poste_recherche', 'statut', 'date_inscription')
    list_filter = ('statut', 'poste_recherche', 'disponibilite')
    search_fields = ('matricule', 'nom', 'prenom', 'telephone')
    readonly_fields = ('matricule', 'date_inscription')
    fieldsets = (
        ('Identification', {
            'fields': ('matricule', 'photo', 'nom', 'prenom', 'age')
        }),
        ('Coordonnées', {
            'fields': ('telephone', 'adresse')
        }),
        ('Profil Professionnel', {
            'fields': ('poste_recherche', 'experience', 'disponibilite', 'statut')
        }),
        ('Notes', {
            'fields': ('observations', 'date_inscription')
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
