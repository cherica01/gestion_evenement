from django.shortcuts import render, get_object_or_404, redirect
from .models import Evenement, Participant
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils.timezone import now
from django.contrib.auth import get_user_model, authenticate, login
from .models import Evenement, Notification
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect

from .models import Evenement, Participant
from django.core.paginator import Paginator

from django.http import JsonResponse

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.core.serializers import serialize

@login_required
def evenement_details(request, id):
    evenement = get_object_or_404(Evenement, id=id, organisateur=request.user)
    data = {
        'titre': evenement.titre,
        'description': evenement.description,
        'lieu': evenement.lieu,
        'date': evenement.date.strftime('%Y-%m-%d'),
        'capacite': evenement.capacite,
    }
    return JsonResponse(data)
def custom_login(request):
    if request.method == 'POST':
        
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Vérifier si les champs sont remplis
        if not username or not password:
            messages.error(request, 'Tous les champs sont requis.')
            return render(request, 'login.html')

        # Récupérer l'utilisateur via son nom d'utilisateur
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

    
        if user is not None:
            login(request, user) 
            # Redirection en fonction du rôle
            if user.role == 'participant':
                return redirect('participant_dashboard')
            elif user.role == 'organisateur':
                return redirect('organisateur_dashboard')
            else:
                messages.error(request, 'Rôle utilisateur non défini.')
        else:
            messages.error(request, 'Nom d\'utilisateur incorrect ou non enregistré.')
            return render(request, 'login.html')
    
    return render(request, 'login.html')


@login_required

def role_required(role):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role != role:
                return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

@login_required
def participant_dashboard(request):
    evenements = Evenement.objects.all()
    for evenement in evenements:
        evenement.est_inscrit = evenement.participants.filter(utilisateur=request.user).exists()

    # Pagination pour les événements
    evenements_paginator = Paginator(evenements, 6)  # 6 événements par page
    evenements_page_number = request.GET.get('evenements_page')
    evenements_page_obj = evenements_paginator.get_page(evenements_page_number)

    # Pagination pour les notifications
    notifications = Notification.objects.filter(
        evenement__participants__utilisateur=request.user
    ).order_by('-date_creation')
    notifications_paginator = Paginator(notifications, 5)  # 5 notifications par page
    notifications_page_number = request.GET.get('notifications_page')
    notifications_page_obj = notifications_paginator.get_page(notifications_page_number)

    return render(request, 'participants_dashboard.html', {
        'evenements': evenements_page_obj,
        'notifications': notifications_page_obj,
    })

# Vue pour le tableau de bord des organisateurs
@login_required
def organisateur_dashboard(request):
    evenements = Evenement.objects.filter(organisateur=request.user)
    paginator = Paginator(evenements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'organisateurs_dashboard.html', {'evenements': page_obj})

# Vue pour créer un nouvel événement
@login_required
def creer_evenement(request):
    if request.method == 'POST':
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        lieu = request.POST.get('lieu')
        date = request.POST.get('date')
        capacite = request.POST.get('capacite')
        programme = request.POST.get('programme')

        Evenement.objects.create(
            titre=titre,
            description=description,
            lieu=lieu,
            date=date,
            capacite=capacite,
            programme=programme,
            organisateur=request.user
        )
        return redirect('organisateur_dashboard')

    return render(request, 'creer_evenement.html')


# Vue pour modifier un événement
@login_required
def modifier_evenement(request, id):
    evenement = get_object_or_404(Evenement, id=id, organisateur=request.user)
    if request.method == 'POST':
        evenement.titre = request.POST.get('titre')
        evenement.description = request.POST.get('description')
        evenement.lieu = request.POST.get('lieu')
        evenement.date = request.POST.get('date')
        evenement.capacite = request.POST.get('capacite')
        evenement.programme = request.POST.get('programme')
        evenement.save()
        return redirect('organisateur_dashboard')

    return render(request, 'modifier_evenement.html', {'evenement': evenement})


# Vue pour supprimer un événement
@login_required
def supprimer_evenement(request, id):
    evenement = get_object_or_404(Evenement, id=id, organisateur=request.user)
    evenement.delete()
    return redirect('organisateur_dashboard')


@login_required
def inscrire_evenement(request, id):
    evenement = get_object_or_404(Evenement, id=id)

    # Vérifie si l'utilisateur est déjà inscrit
    if evenement.participants.filter(utilisateur=request.user).exists():
        messages.info(request, "Vous êtes déjà inscrit à cet événement.")
        return redirect('participant_dashboard')


    if evenement.capacite_restante() <= 0:
        return HttpResponseForbidden("Capacité atteinte.")

    
    Participant.objects.create(utilisateur=request.user, evenement=evenement)
    messages.success(request, "Vous vous êtes inscrit avec succès à l'événement.")
    return redirect('participant_dashboard')



@login_required
def desinscrire_evenement(request, id):
    evenement = get_object_or_404(Evenement, id=id)
    Participant.objects.filter(utilisateur=request.user, evenement=evenement).delete()
    return redirect('participant_dashboard')


@login_required
def participants_evenement(request, id):
    evenement = get_object_or_404(Evenement, id=id, organisateur=request.user)
    participants = evenement.participants.all()
    return render(request, 'participants_list.html', {'evenement': evenement, 'participants': participants})
def envoyer_notification(request, evenement_id):
    evenement = get_object_or_404(Evenement, id=evenement_id, organisateur=request.user)

    if request.method == "POST":
        message = request.POST.get('message')
        est_rappel = request.POST.get('est_rappel') == 'on'

        if message:
            # Créer la notification
            Notification.objects.create(
                evenement=evenement,
                message=message,
                est_rappel=est_rappel
            )
            messages.success(request, "Notification envoyée avec succès.")
        else:
            messages.error(request, "Le message ne peut pas être vide.")
        return redirect('organisateur_dashboard')

    return render(request, 'envoyer_notification.html', {'evenement': evenement})

# Rappels automatiques
def verifier_rappels():
    
    evenements_proches = Evenement.objects.filter(date__lte=now() + timedelta(days=1))
    for evenement in evenements_proches:
    
        if not evenement.notifications.filter(est_rappel=True).exists():
            Notification.objects.create(
                evenement=evenement,
                message=f"Rappel : L'événement {evenement.titre} approche !",
                est_rappel=True
            )
def accueil_participant(request):
    evenements = Evenement.objects.all()
    notifications = Notification.objects.filter(
        evenement__participants__utilisateur=request.user
    ).order_by('-date_creation')

    return render(request, 'accueil_participant.html', {
        'evenements': evenements,
        'notifications': notifications
    })
