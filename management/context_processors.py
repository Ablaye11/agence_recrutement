from .models import Candidat, Notification

def pending_counts(request):
    if request.user.is_authenticated:
        return {
            'pending_validation_count': Candidat.objects.filter(statut='WAITING').count(),
            'unread_notifications_count': Notification.objects.filter(lu=False).count()
        }
    return {'pending_validation_count': 0, 'unread_notifications_count': 0}
