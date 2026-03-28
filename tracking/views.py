import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from clients.models import Culture
from .models import SuiviPousse, StatistiqueCulture
from .forms import SuiviPousseForm, StatistiqueCultureForm
from .stats_engine import calculer_stats_auto, mettre_a_jour_stats
from accounts.decorators import vendeur_or_directeur


@login_required
def suivi_list(request, culture_pk):
    culture = get_object_or_404(Culture, pk=culture_pk)
    suivis = culture.suivis_pousse.all()

    # Calcul automatique des stats
    stats_obj, stats_auto = mettre_a_jour_stats(culture)

    return render(request, 'tracking/suivi_list.html', {
        'culture': culture,
        'suivis': suivis,
        'stats': stats_obj,
        'stats_auto': stats_auto,
        'chart_dates': json.dumps(stats_auto.get('graphique_dates', [])),
        'chart_hauteurs': json.dumps(stats_auto.get('graphique_hauteurs', [])),
        'chart_densites': json.dumps(stats_auto.get('graphique_densites', [])),
        'chart_stades': json.dumps(stats_auto.get('graphique_stades', [])),
        'chart_etats': json.dumps(stats_auto.get('graphique_etats', [])),
        'detail_couts': stats_auto.get('detail_couts', []),
        'cout_par_acre': stats_auto.get('cout_par_acre'),
    })


@vendeur_or_directeur
def suivi_create(request, culture_pk):
    culture = get_object_or_404(Culture, pk=culture_pk)
    if request.method == 'POST':
        form = SuiviPousseForm(request.POST, request.FILES)
        if form.is_valid():
            suivi = form.save(commit=False)
            suivi.culture = culture
            suivi.observateur = request.user
            suivi.save()
            # Recalcul auto des stats
            mettre_a_jour_stats(culture)
            messages.success(request, 'Observation ajoutée.')
            return redirect('tracking:suivi_list', culture_pk=culture.pk)
    else:
        form = SuiviPousseForm()
    return render(request, 'tracking/suivi_form.html', {
        'form': form, 'culture': culture, 'title': 'Nouvelle observation',
    })


@vendeur_or_directeur
def suivi_edit(request, pk):
    suivi = get_object_or_404(SuiviPousse, pk=pk)
    if request.method == 'POST':
        form = SuiviPousseForm(request.POST, request.FILES, instance=suivi)
        if form.is_valid():
            form.save()
            mettre_a_jour_stats(suivi.culture)
            messages.success(request, 'Observation mise à jour.')
            return redirect('tracking:suivi_list', culture_pk=suivi.culture.pk)
    else:
        form = SuiviPousseForm(instance=suivi)
    return render(request, 'tracking/suivi_form.html', {
        'form': form, 'culture': suivi.culture, 'title': "Modifier l'observation",
    })


@vendeur_or_directeur
def stats_edit(request, culture_pk):
    culture = get_object_or_404(Culture, pk=culture_pk)
    stats, created = StatistiqueCulture.objects.get_or_create(culture=culture)
    if request.method == 'POST':
        form = StatistiqueCultureForm(request.POST, instance=stats)
        if form.is_valid():
            form.save()
            messages.success(request, 'Statistiques mises à jour.')
            return redirect('tracking:suivi_list', culture_pk=culture.pk)
    else:
        form = StatistiqueCultureForm(instance=stats)
    return render(request, 'tracking/stats_form.html', {
        'form': form, 'culture': culture, 'title': 'Statistiques de culture',
    })
