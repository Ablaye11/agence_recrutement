from .models import Candidat

def pending_counts(request):
    if request.user.is_authenticated:
        return {
            'pending_validation_count': Candidat.objects.filter(statut='WAITING').count()
        }
    return {'pending_validation_count': 0}
