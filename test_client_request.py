import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_agency.settings')
django.setup()

from management.models import ClientRequest

def run_test():
    print("Simulation d'une commande client...")
    try:
        req = ClientRequest.objects.create(
            nom_client="Test Client Antigravity",
            telephone="77 000 00 00",
            poste_recherche="CUISINE_SEN",
            quartier="Almadies",
            budget_max=150000,
            commentaires="Test de fonctionnement du nouveau portail."
        )
        print(f"✅ Demande créée avec succès ! ID: {req.pk}")
    except Exception as e:
        print(f"❌ Erreur lors de la création : {e}")

if __name__ == "__main__":
    run_test()
