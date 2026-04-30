from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Candidat, Placement

@receiver(post_save, sender=Candidat)
def notify_manager_new_candidat(sender, instance, created, **kwargs):
    if created:
        subject = f"Nouvelle Recrue : {instance.nom} {instance.prenom}"
        message = f"Un nouveau candidat a été enregistré.\nMatricule : {instance.matricule}\nPoste : {instance.get_poste_recherche_display()}\nInscrit le : {instance.date_inscription}"
        try:
            send_mail(subject, message, 'notifications@agence-pro.com', ['admin@votre-agence.com'], fail_silently=True)
        except Exception as e:
            print(f"Erreur d'envoi email : {e}")

@receiver(post_save, sender=Placement)
def notify_manager_placement(sender, instance, created, **kwargs):
    if created:
        subject = f"Nouveau Placement : {instance.candidat.nom} chez {instance.client.nom}"
        message = f"Un placement a été effectué.\nCandidat : {instance.candidat.nom} {instance.candidat.prenom}\nClient : {instance.client.nom}\nSalaire : {instance.salaire} FCFA\nCommission Agence : {instance.commission} FCFA"
        try:
            send_mail(subject, message, 'notifications@agence-pro.com', ['admin@votre-agence.com'], fail_silently=True)
        except Exception as e:
            print(f"Erreur d'envoi email : {e}")
