from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from management.models import Candidat, PreInscription
from unittest.mock import patch

class PreInscriptionPaiementTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Vraie image GIF 1x1 valide pour satisfaire la validation Pillow de ImageField
        tiny_gif = (
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00'
            b',\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        )
        self.dummy_selfie = SimpleUploadedFile("selfie.gif", tiny_gif, content_type="image/gif")
        self.dummy_image_recto = SimpleUploadedFile("cni_recto.jpg", b"fake_recto_bytes", content_type="image/jpeg")
        self.dummy_image_verso = SimpleUploadedFile("cni_verso.jpg", b"fake_verso_bytes", content_type="image/jpeg")

    def test_page_easy_register_chargement(self):
        """Vérifie que la page du formulaire accessible se charge avec succès"""
        response = self.client.get(reverse('easy_register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inscription Facile à l'Emploi")
        self.assertContains(response, "Nounou garde enfant")
        self.assertContains(response, "Femme de ménage")

    @patch('management.views.requests.post')
    def test_candidat_non_enregistre_avant_paiement(self, mock_post):
        """
        Règle d'or :
        Quand le candidat valide le formulaire, il NE DOIT PAS être enregistré dans la table Candidat.
        Il doit être stocké uniquement dans PreInscription avec statut PENDING.
        """
        # Mock de la réponse PayTech
        mock_post.return_value.json.return_value = {
            'success': 1,
            'redirect_url': 'https://paytech.sn/payment/checkout/test-token-123'
        }

        nb_candidats_avant = Candidat.objects.count()
        nb_pre_avant = PreInscription.objects.count()

        data = {
            'poste_recherche': 'NOUNOU',
            'photo': self.dummy_selfie,
            'telephone': '771234567',
            'adresse': 'Grand Yoff',
            'tuteur': 'Ousmane Fall - 770001122',
            'age': 28,
            'email': 'fatou.ndiaye@gmail.com',
            'nom': 'Ndiaye',
            'prenom': 'Fatou',
            'piece_identite': self.dummy_image_recto,
            'piece_identite_verso': self.dummy_image_verso,
        }

        response = self.client.post(reverse('easy_register'), data, follow=False)

        # Redirection vers PayTech
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://paytech.sn/payment/checkout/test-token-123')

        # VÉRIFICATION CRUCIALE : La table Candidat n'a PAS augmenté !
        self.assertEqual(Candidat.objects.count(), nb_candidats_avant)

        # Seule la table temporaire a été incrémentée
        self.assertEqual(PreInscription.objects.count(), nb_pre_avant + 1)
        pre = PreInscription.objects.latest('id')
        self.assertEqual(pre.statut_paiement, 'PENDING')
        self.assertEqual(pre.telephone, '771234567')
        self.assertEqual(pre.tuteur, 'Ousmane Fall - 770001122')

    def test_candidat_enregistre_apres_paiement_valide(self):
        """
        Vérifie qu'une fois le paiement validé (IPN PayTech ou confirmation),
        les informations sont bien transférées dans la table Candidat.
        """
        # Création d'une pré-inscription en attente
        pre = PreInscription.objects.create(
            ref_command='DT-TEST-REF-999',
            poste_recherche='MENAGE',
            telephone='789998877',
            adresse='Pikine Icotaf',
            tuteur='Aminata Sow - 771112233',
            nom='Diallo',
            prenom='Mariama',
            statut_paiement='PENDING',
        )

        nb_candidats_avant = Candidat.objects.count()

        # Simulation de l'appel IPN de PayTech confirmant le paiement
        response = self.client.post(reverse('payment_ipn'), {
            'ref_command': 'DT-TEST-REF-999',
            'token': 'PAYTECH_TOKEN_SUCCESS_999'
        })

        self.assertEqual(response.status_code, 200)

        # Le candidat doit MAINTENANT être créé dans Candidat avec frais_paye=True
        self.assertEqual(Candidat.objects.count(), nb_candidats_avant + 1)
        candidat = Candidat.objects.get(transaction_id='PAYTECH_TOKEN_SUCCESS_999')
        self.assertEqual(candidat.telephone, '789998877')
        self.assertEqual(candidat.nom, 'Diallo')
        self.assertEqual(candidat.prenom, 'Mariama')
        self.assertEqual(candidat.tuteur, 'Aminata Sow - 771112233')
        self.assertTrue(candidat.frais_paye)
        self.assertEqual(candidat.statut, 'WAITING')
