from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.http import HttpResponse, FileResponse
import openpyxl
from openpyxl.styles import Font, PatternFill
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from .models import Candidat, Client, Placement, Notification, Expense, ClientRequest
from django.core.mail import send_mail
from django.conf import settings
from .forms import CandidatForm, ClientForm, PlacementForm, RegistrationForm, ClientRequestForm
from datetime import date, datetime, timedelta
import json
from django.core.exceptions import PermissionDenied

def admin_only(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "Accès réservé à l'administrateur.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

# --- AUTHENTICATION ---
def login_view(request):
    if request.user.is_authenticated: return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user: login(request, user); return redirect('dashboard')
    return render(request, 'management/login.html', {'form': AuthenticationForm()})

def logout_view(request): logout(request); return redirect('logout_success')
def logout_success_view(request): return render(request, 'management/logout_success.html')

# --- DASHBOARD & STATS ---
@login_required
def dashboard(request):
    total_revenus = Placement.objects.filter(est_paye=True).aggregate(Sum('commission'))['commission__sum'] or 0
    total_depenses = Expense.objects.aggregate(Sum('montant'))['montant__sum'] or 0
    postes_stats = Candidat.objects.values('poste_recherche').annotate(total=Count('id'))
    
    context = {
        'total_candidats': Candidat.objects.count(),
        'total_places': Candidat.objects.filter(statut='PLACED').count(),
        'total_dispo': Candidat.objects.filter(statut='AVAILABLE').count(),
        'total_attente': Candidat.objects.filter(statut='WAITING').count(),
        'total_revenus': total_revenus,
        'benefice_net': total_revenus - total_depenses,
        'labels_poste': json.dumps([str(dict(Candidat.POSTE_CHOICES).get(p['poste_recherche'])) for p in postes_stats]),
        'data_poste': json.dumps([p['total'] for p in postes_stats]),
        'recent_candidats': Candidat.objects.order_by('-date_inscription')[:5],
        'recent_placements': Placement.objects.order_by('-date_placement')[:5],
    }
    return render(request, 'management/dashboard.html', context)

@login_required
def statistics(request):
    stats_poste = Candidat.objects.values('poste_recherche').annotate(total=Count('id'))
    stats_statut = Candidat.objects.values('statut').annotate(total=Count('id'))
    
    # Evolution (last 6 months)
    labels_evo, data_evo = [], []
    for i in range(5, -1, -1):
        d = date.today() - timedelta(days=i*30)
        month_label = d.strftime("%b %Y")
        count = Candidat.objects.filter(date_inscription__month=d.month, date_inscription__year=d.year).count()
        labels_evo.append(month_label); data_evo.append(count)

    context = {
        'labels_poste': json.dumps([str(dict(Candidat.POSTE_CHOICES).get(s['poste_recherche'])) for s in stats_poste]),
        'data_poste': json.dumps([s['total'] for s in stats_poste]),
        'labels_statut': json.dumps([str(dict(Candidat.STATUT_CHOICES).get(s['statut'])) for s in stats_statut]),
        'data_statut': json.dumps([s['total'] for s in stats_statut]),
        'labels_evo': json.dumps(labels_evo),
        'data_evo': json.dumps(data_evo),
    }
    return render(request, 'management/statistics.html', context)

# --- CANDIDATS ---
@login_required
def inscriptions_en_attente(request):
    candidats = Candidat.objects.filter(statut='WAITING').order_by('-date_inscription')
    return render(request, 'management/inscriptions_en_attente.html', {'candidats': candidats})

@login_required
def candidat_list(request):
    candidats = Candidat.objects.all()
    q = request.GET.get('q'); s = request.GET.get('statut'); p = request.GET.get('poste')
    if q: candidats = candidats.filter(Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(telephone__icontains=q))
    if s: candidats = candidats.filter(statut=s)
    if p: candidats = candidats.filter(poste_recherche=p)
    # Récupération des choix de métiers pour le filtre
    poste_choices = Candidat.POSTE_CHOICES
    
    return render(request, 'management/candidat_list.html', {
        'candidats': candidats,
        'poste_choices': poste_choices
    })

@login_required
@admin_only
def candidat_bulk_action(request):
    if request.method == 'POST':
        ids = request.POST.getlist('selected_ids')
        action = request.POST.get('action')
        if ids and action:
            candidats = Candidat.objects.filter(pk__in=ids)
            if action == 'delete':
                candidats.delete()
                messages.success(request, f"{len(ids)} candidats supprimés.")
            elif action == 'status_available':
                candidats.update(statut='AVAILABLE')
                messages.success(request, f"{len(ids)} candidats passés en 'Disponible'.")
            elif action == 'status_waiting':
                candidats.update(statut='WAITING')
                messages.success(request, f"{len(ids)} candidats passés en 'En attente'.")
    return redirect('candidat_list')

@login_required
def candidat_detail(request, pk):
    return render(request, 'management/candidat_detail.html', {'candidat': get_object_or_404(Candidat, pk=pk)})

@login_required
def candidat_create(request):
    if request.method == 'POST':
        form = CandidatForm(request.POST, request.FILES)
        if form.is_valid():
            c = form.save(); Notification.objects.create(titre="Nouveau candidat", message=f"{c.nom} {c.prenom} ajouté.", type_notif='SUCCESS')
            return redirect('candidat_list')
    return render(request, 'management/candidat_form.html', {'form': CandidatForm(), 'title': 'Ajouter un candidat'})

@login_required
def candidat_edit(request, pk):
    c = get_object_or_404(Candidat, pk=pk)
    if request.method == 'POST':
        form = CandidatForm(request.POST, request.FILES, instance=c)
        if form.is_valid(): form.save(); return redirect('candidat_detail', pk=c.pk)
    return render(request, 'management/candidat_form.html', {'form': CandidatForm(instance=c), 'title': 'Modifier'})

@login_required
@admin_only
def candidat_delete(request, pk): get_object_or_404(Candidat, pk=pk).delete(); return redirect('candidat_list')

@login_required
def candidat_approve(request, pk):
    c = get_object_or_404(Candidat, pk=pk)
    if c.statut == 'WAITING':
        c.statut = 'AVAILABLE'; c.save()
        Notification.objects.create(titre="Validé", message=f"{c.nom} est maintenant disponible.", type_notif='SUCCESS')
    return redirect('candidat_detail', pk=c.pk)

def candidat_public_register(request):
    if request.method == 'POST':
        form = CandidatForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False); obj.statut = 'WAITING'; obj.save()
            Notification.objects.create(titre="Inscription en ligne", message=f"Nouveau candidat : {obj.nom} {obj.prenom}", type_notif='WARNING')
            
            # Envoi du mail
            try:
                send_mail(
                    'Nouvelle inscription candidat',
                    f"Un nouveau candidat vient de s'inscrire : {obj.nom} {obj.prenom}\nPoste : {obj.get_poste_recherche_display()}\nTéléphone : {obj.telephone}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"--- ERREUR EMAIL : {e} ---")
            
            return render(request, 'management/public_success.html')
    return render(request, 'management/public_register.html', {'form': CandidatForm()})

# --- CLIENTS & CRM ---
@login_required
def client_list(request): return render(request, 'management/client_list.html', {'clients': Client.objects.all().order_by('nom')})

@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    placements = client.placements.all().order_by('-date_placement')
    total_paye = placements.filter(est_paye=True).aggregate(Sum('commission'))['commission__sum'] or 0
    return render(request, 'management/client_detail.html', {'client': client, 'placements': placements, 'total_paye': total_paye})

@login_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid(): form.save(); return redirect('client_list')
    return render(request, 'management/client_form.html', {'form': ClientForm()})

@login_required
@admin_only
def client_delete(request, pk): get_object_or_404(Client, pk=pk).delete(); return redirect('client_list')

# --- PLACEMENTS ---
@login_required
def placement_history(request):
    placements = Placement.objects.filter(statut_emploi='TERMINATED').order_by('-date_fin')
    return render(request, 'management/placement_list.html', {'placements': placements, 'is_history': True})

@login_required
def placement_list(request):
    return render(request, 'management/placement_list.html', {'placements': Placement.objects.filter(statut_emploi='ACTIVE').order_by('-date_placement')})

@login_required
def placement_create(request):
    if request.method == 'POST':
        form = PlacementForm(request.POST)
        if form.is_valid():
            p = form.save(); p.candidat.statut = 'PLACED'; p.candidat.save()
            Notification.objects.create(titre="Placement", message=f"{p.candidat.nom} chez {p.client.nom}.", type_notif='INFO')
            
            # Envoi du mail
            try:
                send_mail(
                    'Nouveau placement effectué',
                    f"Un placement a été enregistré :\nCandidat : {p.candidat}\nClient : {p.client}\nCommission : {p.commission} FCFA",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"--- ERREUR EMAIL PLACEMENT : {e} ---")
            
            return redirect('placement_list')
    return render(request, 'management/placement_form.html', {'form': PlacementForm(initial={'candidat': request.GET.get('candidat')})})

@login_required
def placement_edit(request, pk):
    p = get_object_or_404(Placement, pk=pk)
    if request.method == 'POST':
        form = PlacementForm(request.POST, instance=p)
        if form.is_valid(): form.save(); return redirect('placement_list')
    return render(request, 'management/placement_form.html', {'form': PlacementForm(instance=p)})

@login_required
def placement_terminate(request, pk):
    p = get_object_or_404(Placement, pk=pk)
    if p.statut_emploi == 'ACTIVE':
        p.statut_emploi = 'TERMINATED'; p.date_fin = date.today(); p.save()
        p.candidat.statut = 'AVAILABLE'; p.candidat.save()
    return redirect('placement_list')

# --- FINANCE & EXPENSES ---
@login_required
@admin_only
def finance_reports(request):
    revenus_qs = Placement.objects.filter(est_paye=True).values('date_paiement__month').annotate(total=Sum('commission')).order_by('date_paiement__month')
    depenses_qs = Expense.objects.values('date_depense__month').annotate(total=Sum('montant')).order_by('date_depense__month')
    
    rev_total = Placement.objects.filter(est_paye=True).aggregate(Sum('commission'))['commission__sum'] or 0
    dep_total = Expense.objects.aggregate(Sum('montant'))['montant__sum'] or 0
    
    context = {
        'revenus': revenus_qs, 'depenses': depenses_qs,
        'benefice_net': rev_total - dep_total,
        'js_labels': json.dumps([f"Mois {r['date_paiement__month']}" for r in revenus_qs]),
        'js_data': json.dumps([float(r['total']) for r in revenus_qs]),
        'top_clients': Client.objects.annotate(n=Count('placements')).order_by('-n')[:5]
    }
    return render(request, 'management/reports.html', context)

@login_required
@admin_only
def expense_list(request):
    return render(request, 'management/expense_list.html', {'expenses': Expense.objects.all(), 'total': Expense.objects.aggregate(Sum('montant'))['montant__sum'] or 0})

@login_required
@admin_only
def expense_create(request):
    if request.method == 'POST':
        Expense.objects.create(
            titre=request.POST.get('titre'),
            categorie=request.POST.get('categorie'),
            montant=request.POST.get('montant'),
            date_depense=request.POST.get('date_depense') or date.today()
        )
        return redirect('expense_list')
    return render(request, 'management/expense_form.html')

@login_required
def candidat_print(request, pk):
    candidat = get_object_or_404(Candidat, pk=pk)
    return render(request, 'management/candidat_print.html', {'candidat': candidat})

@login_required
def placement_print(request, pk):
    placement = get_object_or_404(Placement, pk=pk)
    return render(request, 'management/placement_print.html', {'placement': placement})

# --- API & UTILS ---
@login_required
def pending_validation_count(request): return render(request, 'management/partials/pending_badge.html', {'count': Candidat.objects.filter(statut='WAITING').count()})

@login_required
def get_notifications(request): return render(request, 'management/partials/notifications.html', {'notifs': Notification.objects.filter(lu=False)[:5]})

@login_required
def export_candidats_excel(request):
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Candidats"
    ws.append(['Nom', 'Prénom', 'Âge', 'Téléphone', 'Poste', 'Statut'])
    for c in Candidat.objects.all(): ws.append([c.nom, c.prenom, c.age, c.telephone, c.get_poste_recherche_display(), c.get_statut_display()])
    res = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    res['Content-Disposition'] = 'attachment; filename=candidats.xlsx'; wb.save(res); return res

@login_required
def generate_contract_pdf(request, pk):
    p = get_object_or_404(Placement, pk=pk)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    # --- Design & Cadre ---
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(1*cm, 1*cm, width-2*cm, height-2*cm) # Cadre de page

    # --- En-tête ---
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, 28*cm, "REPUBLIQUE DU SENEGAL")
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, 27*cm, "DAKAR TERMINUS")
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, 26*cm, "CONTRAT DE PLACEMENT")
    c.setLineWidth(2)
    c.line(2*cm, 26.5*cm, width-2*cm, 26.5*cm)

    # --- Informations ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, 25*cm, "1. LES PARTIES")
    
    c.setFont("Helvetica", 12)
    c.drawString(2.5*cm, 24*cm, f"L'EMPLOYEUR : {p.client.nom.upper()}")
    c.drawString(2.5*cm, 23.3*cm, f"Téléphone : {p.client.telephone}")
    
    c.drawString(2.5*cm, 22*cm, f"L'EMPLOYÉ(E) : {p.candidat.nom.upper()} {p.candidat.prenom}")
    c.drawString(2.5*cm, 21.3*cm, f"Poste : {p.candidat.get_poste_recherche_display()}")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, 19*cm, "2. CONDITIONS DU CONTRAT")
    
    c.setFont("Helvetica", 12)
    c.drawString(2.5*cm, 18*cm, f"Lieu de travail : {p.lieu_travail}")
    c.drawString(2.5*cm, 17.3*cm, f"Date de début : {p.date_debut.strftime('%d/%m/%Y')}")
    c.drawString(2.5*cm, 16.6*cm, f"Salaire mensuel : {p.salaire} FCFA")
    c.drawString(2.5*cm, 15.9*cm, f"Statut : {p.get_statut_emploi_display()}")

    # --- Signatures ---
    c.line(2*cm, 10*cm, width-2*cm, 10*cm)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, 9*cm, "SIGNATURE EMPLOYEUR")
    c.drawString(width-8*cm, 9*cm, "SIGNATURE EMPLOYÉ(E)")
    
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(2*cm, 4*cm, f"Fait à Dakar, le {date.today().strftime('%d/%m/%Y')}")
    c.drawCentredString(width/2, 2*cm, "Document généré par DAKAR TERMINUS Management System")

    c.showPage()
    c.save()
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=f"contrat_{p.pk}.pdf")

@login_required
def unpaid_commissions(request):
    unpaid = Placement.objects.filter(est_paye=False).order_by('-date_placement')
    return render(request, 'management/unpaid_commissions.html', {'unpaid': unpaid, 'total_due': unpaid.aggregate(Sum('commission'))['commission__sum'] or 0})

@login_required
@admin_only
def client_request_accept(request, pk):
    req = get_object_or_404(ClientRequest, pk=pk)
    # Création du client officiel
    Client.objects.create(
        nom=req.nom_client,
        telephone=req.telephone,
        adresse=req.quartier
    )
    # On marque la demande comme traitée ou on la supprime
    req.delete() 
    messages.success(request, f"Le client {req.nom_client} a été ajouté avec succès !")
    return redirect('client_list')

@login_required
def client_request_list(request):
    requests = ClientRequest.objects.all()
    return render(request, 'management/client_request_list.html', {'client_requests': requests})

@login_required
@admin_only
def client_request_delete(request, pk):
    get_object_or_404(ClientRequest, pk=pk).delete()
    return redirect('client_request_list')

def client_public_request(request):
    if request.method == 'POST':
        form = ClientRequestForm(request.POST)
        if form.is_valid():
            obj = form.save()
            Notification.objects.create(titre="Nouvelle commande client", message=f"Besoin de : {obj.get_poste_recherche_display()} par {obj.nom_client}", type_notif='INFO')
            
            # Envoi du mail
            try:
                send_mail(
                    'NOUVELLE COMMANDE CLIENT',
                    f"Un client vient de faire une demande :\nClient : {obj.nom_client}\nPoste : {obj.get_poste_recherche_display()}\nZone : {obj.quartier}\nBudget : {obj.budget_max} FCFA\nContact : {obj.telephone}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"--- ERREUR MAIL COMMANDE : {e} ---")
            
            return render(request, 'management/client_request_success.html')
    return render(request, 'management/client_public_request.html', {'form': ClientRequestForm()})