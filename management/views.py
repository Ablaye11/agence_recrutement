from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .models import Candidat, Client, Placement
from django.db.models import Q, Count, Sum
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

from django.db.models import Count, Sum

@login_required
def statistics(request):
    # Répartition par poste
    stats_poste = Candidat.objects.values('poste_recherche').annotate(total=Count('id'))
    labels_poste = [str(dict(Candidat.POSTE_CHOICES).get(s['poste_recherche'], s['poste_recherche'])) for s in stats_poste]
    data_poste = [s['total'] for s in stats_poste]

    # Répartition par statut
    stats_statut = Candidat.objects.values('statut').annotate(total=Count('id'))
    labels_statut = [str(dict(Candidat.STATUT_CHOICES).get(s['statut'], s['statut'])) for s in stats_statut]
    data_statut = [s['total'] for s in stats_statut]

    # Évolution des inscriptions (6 derniers mois)
    from django.db.models.functions import TruncMonth
    import datetime
    six_months_ago = datetime.date.today() - datetime.timedelta(days=180)
    stats_evolution = Candidat.objects.filter(date_inscription__gte=six_months_ago)\
        .annotate(month=TruncMonth('date_inscription'))\
        .values('month')\
        .annotate(total=Count('id'))\
        .order_by('month')
    
    labels_evo = [s['month'].strftime("%b %Y") for s in stats_evolution]
    data_evo = [s['total'] for s in stats_evolution]

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
    
    # Calcul des revenus (somme des commissions payées)
    total_revenus = Placement.objects.filter(est_paye=True).aggregate(Sum('commission'))['commission__sum'] or 0

    # Données pour Chart.js (Répartition par poste)
    postes_stats = Candidat.objects.values('poste_recherche').annotate(total=Count('poste_recherche'))
    labels_poste = [p['poste_recherche'] for p in postes_stats]
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
    adresse_query = request.GET.get('adresse')
    
    candidats = Candidat.objects.all()
    
    if query:
        candidats = candidats.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query) | 
            Q(telephone__icontains=query) |
            Q(adresse__icontains=query)
        )
    if adresse_query:
        candidats = candidats.filter(adresse__icontains=adresse_query)
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

from .forms import CandidatForm, ClientForm, PlacementForm

@login_required
def candidat_create(request):
    if request.method == 'POST':
        form = CandidatForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
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
            # Mettre à jour le statut du candidat
            candidat = placement.candidat
            candidat.statut = 'PLACED'
            candidat.save()
            return redirect('placement_list')
    else:
        form = PlacementForm(initial=initial_data)
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
def placement_edit(request, pk):
    placement = get_object_or_404(Placement, pk=pk)
    if request.method == 'POST':
        form = PlacementForm(request.POST, instance=placement)
        if form.is_valid():
            form.save()
            return redirect('placement_list')
    else:
        form = PlacementForm(instance=placement)
    return render(request, 'management/placement_form.html', {'form': form, 'title': 'Modifier le placement'})

@login_required
def placement_terminate(request, pk):
    placement = get_object_or_404(Placement, pk=pk)
    if placement.statut_emploi == 'ACTIVE':
        # Marquer le contrat comme terminé
        placement.statut_emploi = 'TERMINATED'
        import datetime
        placement.date_fin = datetime.date.today()
        placement.save()
        
        # Libérer le candidat
        candidat = placement.candidat
        candidat.statut = 'AVAILABLE'
        candidat.save()
        
    return redirect('placement_list')

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
def finance_reports(request):
    from django.db.models.functions import ExtractMonth
    import json
    
    # Revenus par mois
    revenus_qs = Placement.objects.filter(est_paye=True).annotate(
        month=ExtractMonth('date_paiement')
    ).values('month').annotate(total=Sum('commission')).order_by('month')
    
    # Préparation des données pour JS
    labels = [f"Mois {r['month']}" for r in revenus_qs]
    data = [float(r['total']) for r in revenus_qs]
    
    # Meilleurs clients
    top_clients = Client.objects.annotate(num_placements=Count('placements')).order_by('-num_placements')[:5]
    
    return render(request, 'management/reports.html', {
        'revenus_mensuels': revenus_qs,
        'top_clients': top_clients,
        'js_labels': json.dumps(labels),
        'js_data': json.dumps(data),
    })

@login_required
def candidat_print(request, pk):
    candidat = get_object_or_404(Candidat, pk=pk)
    return render(request, 'management/candidat_print.html', {'candidat': candidat})

@login_required
def placement_print(request, pk):
    placement = get_object_or_404(Placement, pk=pk)
    return render(request, 'management/placement_print.html', {'placement': placement})

@login_required
def pending_validation_count(request):
    count = Candidat.objects.filter(statut='WAITING').count()
    if count > 0:
        return render(request, 'management/partials/pending_badge.html', {'count': count})
    return render(request, 'management/partials/pending_badge.html', {'count': 0})

@login_required
def candidat_approve(request, pk):
    candidat = get_object_or_404(Candidat, pk=pk)
    if candidat.statut == 'WAITING':
        candidat.statut = 'AVAILABLE'
        candidat.save()
    return redirect('candidat_detail', pk=candidat.pk)

def candidat_public_register(request):
    if request.method == 'POST':
        form = CandidatForm(request.POST, request.FILES)
        if form.is_valid():
            candidat = form.save(commit=False)
            candidat.statut = 'WAITING'
            candidat.save()
            return render(request, 'management/public_success.html')
    else:
        form = CandidatForm()
        if 'statut' in form.fields: del form.fields['statut']
        if 'observations' in form.fields: del form.fields['observations']
        
    return render(request, 'management/public_register.html', {'form': form})
