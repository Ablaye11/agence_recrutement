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
from .models import Candidat, Client, Placement, Notification
from .forms import CandidatForm, ClientForm, PlacementForm, RegistrationForm
from datetime import date, datetime
import json

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'management/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('logout_success')

def logout_success_view(request):
    return render(request, 'management/logout_success.html')

@login_required
def statistics(request):
    stats_poste = Candidat.objects.values('poste_recherche').annotate(total=Count('id'))
    labels_poste = [str(dict(Candidat.POSTE_CHOICES).get(s['poste_recherche'], s['poste_recherche'])) for s in stats_poste]
    data_poste = [s['total'] for s in stats_poste]

    stats_statut = Candidat.objects.values('statut').annotate(total=Count('id'))
    labels_statut = [str(dict(Candidat.STATUT_CHOICES).get(s['statut'], s['statut'])) for s in stats_statut]
    data_statut = [s['total'] for s in stats_statut]

    from django.db.models.functions import TruncMonth
    six_months_ago = date.today() - datetime.timedelta(days=180) if hasattr(datetime, 'timedelta') else date.today()
    # Simplified for now to avoid date errors
    stats_evolution = Candidat.objects.all().order_by('date_inscription')[:10]
    
    labels_evo = [s.date_inscription.strftime("%d/%m") for s in stats_evolution]
    data_evo = [i for i in range(1, len(stats_evolution)+1)]

    context = {
        'labels_poste': json.dumps(labels_poste),
        'data_poste': json.dumps(data_poste),
        'labels_statut': json.dumps(labels_statut),
        'data_statut': json.dumps(data_statut),
        'labels_evo': json.dumps(labels_evo),
        'data_evo': json.dumps(data_evo),
    }
    return render(request, 'management/statistics.html', context)

@login_required
def dashboard(request):
    total_candidats = Candidat.objects.count()
    total_places = Candidat.objects.filter(statut='PLACED').count()
    total_dispo = Candidat.objects.filter(statut='AVAILABLE').count()
    total_attente = Candidat.objects.filter(statut='WAITING').count()
    total_revenus = Placement.objects.filter(est_paye=True).aggregate(Sum('commission'))['commission__sum'] or 0

    postes_stats = Candidat.objects.values('poste_recherche').annotate(total=Count('poste_recherche'))
    labels_poste = [str(dict(Candidat.POSTE_CHOICES).get(p['poste_recherche'], p['poste_recherche'])) for p in postes_stats]
    data_poste = [p['total'] for p in postes_stats]

    context = {
        'total_candidats': total_candidats,
        'total_places': total_places,
        'total_dispo': total_dispo,
        'total_attente': total_attente,
        'total_revenus': total_revenus,
        'labels_poste': json.dumps(labels_poste),
        'data_poste': json.dumps(data_poste),
        'recent_candidats': Candidat.objects.order_by('-date_inscription')[:5],
        'recent_placements': Placement.objects.order_by('-date_placement')[:5],
    }
    return render(request, 'management/dashboard.html', context)

@login_required
def candidat_list(request):
    query = request.GET.get('q')
    statut = request.GET.get('statut')
    poste = request.GET.get('poste')
    candidats = Candidat.objects.all()
    if query:
        candidats = candidats.filter(Q(nom__icontains=query) | Q(prenom__icontains=query) | Q(telephone__icontains=query))
    if statut:
        candidats = candidats.filter(statut=statut)
    if poste:
        candidats = candidats.filter(poste_recherche=poste)
    return render(request, 'management/candidat_list.html', {'candidats': candidats})

@login_required
def inscriptions_en_attente(request):
    candidats = Candidat.objects.filter(statut='WAITING').order_by('-date_inscription')
    return render(request, 'management/inscriptions_en_attente.html', {'candidats': candidats})

@login_required
def candidat_detail(request, pk):
    candidat = get_object_or_404(Candidat, pk=pk)
    return render(request, 'management/candidat_detail.html', {'candidat': candidat})

@login_required
def candidat_create(request):
    if request.method == 'POST':
        form = CandidatForm(request.POST, request.FILES)
        if form.is_valid():
            candidat = form.save()
            Notification.objects.create(titre="Nouveau candidat", message=f"{candidat.nom} {candidat.prenom} a été ajouté.", type_notif='SUCCESS')
            return redirect('candidat_list')
    else:
        form = CandidatForm()
    return render(request, 'management/candidat_form.html', {'form': form, 'title': 'Ajouter un candidat'})

@login_required
def candidat_edit(request, pk):
    candidat = get_object_or_404(Candidat, pk=pk)
    if request.method == 'POST':
        form = CandidatForm(request.POST, request.FILES, instance=candidat)
        if form.is_valid():
            form.save()
            return redirect('candidat_detail', pk=candidat.pk)
    else:
        form = CandidatForm(instance=candidat)
    return render(request, 'management/candidat_form.html', {'form': form, 'title': 'Modifier le candidat'})

@login_required
def placement_create(request):
    candidat_id = request.GET.get('candidat')
    initial_data = {}
    if candidat_id:
        initial_data['candidat'] = candidat_id
    if request.method == 'POST':
        form = PlacementForm(request.POST)
        if form.is_valid():
            placement = form.save()
            candidat = placement.candidat
            candidat.statut = 'PLACED'
            candidat.save()
            Notification.objects.create(titre="Nouveau placement", message=f"Placement de {candidat.nom} chez {placement.client.nom}.", type_notif='INFO')
            return redirect('placement_list')
    else:
        form = PlacementForm(initial=initial_data)
    return render(request, 'management/placement_form.html', {'form': form})

@login_required
def placement_edit(request, pk):
    placement = get_object_or_404(Placement, pk=pk)
    if request.method == 'POST':
        form = PlacementForm(request.POST, instance=placement)
        if form.is_valid():
            form.save()
            return redirect('placement_list')
    else:
        form = PlacementForm(instance=placement)
    return render(request, 'management/placement_form.html', {'form': form})

@login_required
def placement_list(request):
    placements = Placement.objects.filter(statut_emploi='ACTIVE').order_by('-date_placement')
    return render(request, 'management/placement_list.html', {'placements': placements})

@login_required
def placement_history(request):
    history = Placement.objects.filter(statut_emploi='TERMINATED').order_by('-date_fin')
    return render(request, 'management/placement_history.html', {'history': history})

@login_required
def placement_terminate(request, pk):
    placement = get_object_or_404(Placement, pk=pk)
    if placement.statut_emploi == 'ACTIVE':
        placement.statut_emploi = 'TERMINATED'
        placement.date_fin = date.today()
        placement.save()
        candidat = placement.candidat
        candidat.statut = 'AVAILABLE'
        candidat.save()
    return redirect('placement_list')

@login_required
def client_list(request):
    clients = Client.objects.all().order_by('nom')
    return render(request, 'management/client_list.html', {'clients': clients})

@login_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, 'management/client_form.html', {'form': form})

@login_required
def candidat_delete(request, pk):
    candidat = get_object_or_404(Candidat, pk=pk)
    candidat.delete()
    return redirect('candidat_list')

@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.delete()
    return redirect('client_list')

@login_required
def candidat_print(request, pk):
    candidat = get_object_or_404(Candidat, pk=pk)
    return render(request, 'management/candidat_print.html', {'candidat': candidat})

@login_required
def placement_print(request, pk):
    placement = get_object_or_404(Placement, pk=pk)
    return render(request, 'management/placement_print.html', {'placement': placement})

@login_required
def finance_reports(request):
    from django.db.models.functions import ExtractMonth
    revenus_qs = Placement.objects.filter(est_paye=True).annotate(month=ExtractMonth('date_paiement')).values('month').annotate(total=Sum('commission')).order_by('month')
    labels = [f"Mois {r['month']}" for r in revenus_qs]
    data = [float(r['total']) for r in revenus_qs]
    top_clients = Client.objects.annotate(num_placements=Count('placements')).order_by('-num_placements')[:5]
    return render(request, 'management/reports.html', {'revenus_mensuels': revenus_qs, 'top_clients': top_clients, 'js_labels': json.dumps(labels), 'js_data': json.dumps(data)})

@login_required
def pending_validation_count(request):
    count = Candidat.objects.filter(statut='WAITING').count()
    return render(request, 'management/partials/pending_badge.html', {'count': count})

@login_required
def candidat_approve(request, pk):
    candidat = get_object_or_404(Candidat, pk=pk)
    if candidat.statut == 'WAITING':
        candidat.statut = 'AVAILABLE'
        candidat.save()
        Notification.objects.create(titre="Candidat validé", message=f"Le dossier de {candidat.nom} a été approuvé.", type_notif='SUCCESS')
    return redirect('candidat_detail', pk=candidat.pk)

def candidat_public_register(request):
    if request.method == 'POST':
        form = CandidatForm(request.POST, request.FILES)
        if form.is_valid():
            candidat = form.save(commit=False)
            candidat.statut = 'WAITING'
            candidat.save()
            Notification.objects.create(titre="Nouvelle inscription", message=f"Un nouveau candidat s'est inscrit en ligne.", type_notif='WARNING')
            return render(request, 'management/public_success.html')
    else:
        form = CandidatForm()
    return render(request, 'management/public_register.html', {'form': form})

@login_required
def unpaid_commissions(request):
    unpaid = Placement.objects.filter(est_paye=False).order_by('-date_placement')
    total_due = unpaid.aggregate(Sum('commission'))['commission__sum'] or 0
    return render(request, 'management/unpaid_commissions.html', {'unpaid': unpaid, 'total_due': total_due})

@login_required
def export_candidats_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Candidats"
    headers = ['Nom', 'Prénom', 'Âge', 'Téléphone', 'Adresse', 'Poste', 'Statut']
    ws.append(headers)
    for c in Candidat.objects.all():
        ws.append([c.nom, c.prenom, c.age, c.telephone, c.adresse, c.get_poste_recherche_display(), c.get_statut_display()])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=candidats.xlsx'
    wb.save(response)
    return response

@login_required
def get_notifications(request):
    notifs = Notification.objects.filter(lu=False)[:5]
    return render(request, 'management/partials/notifications.html', {'notifs': notifs})

@login_required
def generate_contract_pdf(request, pk):
    placement = get_object_or_404(Placement, pk=pk)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(2*cm, 27*cm, "CONTRAT DE PLACEMENT")
    p.setFont("Helvetica", 12)
    p.drawString(2*cm, 25*cm, f"Employeur : {placement.client.nom}")
    p.drawString(2*cm, 24*cm, f"Candidat : {placement.candidat.nom} {placement.candidat.prenom}")
    p.drawString(2*cm, 23*cm, f"Poste : {placement.candidat.get_poste_recherche_display()}")
    p.drawString(2*cm, 22*cm, f"Salaire : {placement.salaire} FCFA")
    p.drawString(2*cm, 21*cm, f"Lieu : {placement.lieu_travail}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"contrat_{placement.pk}.pdf")