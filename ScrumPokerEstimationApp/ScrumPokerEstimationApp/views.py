import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.db import IntegrityError
from .models import Partie, Joueur
import uuid
import random
import string

def home(request):
    return render(request, 'home.html')

def generer_code_unique():
    """Génère un code unique de 5 caractères (chiffres et lettres)."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

def lancer_partie(request):
    if request.method == 'POST':
        mode = request.POST.get('mode')
        if not mode:
            return JsonResponse({'error': 'Le mode de jeu doit être sélectionné.'}, status=400)

        # Récupérer le nombre de joueurs
        nb_joueurs = int(request.POST.get('nb_joueurs'))
        if nb_joueurs < 1 or nb_joueurs > 10:
            return JsonResponse({'error': 'Le nombre de joueurs doit être compris entre 1 et 10.'}, status=400)

        # Récupérer les pseudos des joueurs et vérifier qu'ils sont uniques
        pseudos = []
        for i in range(1, nb_joueurs + 1):
            pseudo = request.POST.get(f'player_{i}')
            if pseudo in pseudos:
                return JsonResponse({'error': f'Le pseudo "{pseudo}" est déjà pris.'}, status=400)
            pseudos.append(pseudo)

        # Récupérer le nombre de tâches
        nb_taches = int(request.POST.get('nb_taches'))
        if nb_taches < 1:
            return JsonResponse({'error': 'Le nombre de tâches doit être supérieur à 0.'}, status=400)

        # Récupérer les intitulés des tâches
        backlog = []
        for i in range(1, nb_taches + 1):
            tache = request.POST.get(f'tache_{i}')
            if not tache:
                return JsonResponse({'error': f'L\'intitulé de la tâche {i} est requis.'}, status=400)
            backlog.append({
                "id": str(uuid.uuid4()),
                "description": tache.strip(),
                "date_created": timezone.now().isoformat()
            })

        # Vérifier que le backlog n'est pas vide
        if not backlog:
            return JsonResponse({'error': 'Veuillez décrire au moins une tâche.'}, status=400)

        # Générer un code unique pour la partie
        code_unique = generer_code_unique()
        while Partie.objects.filter(code=code_unique).exists():
            code_unique = generer_code_unique()

        # Créer la partie avec les joueurs et la tâche
        try:
            partie = Partie.objects.create(code=code_unique, mode=mode, backlog=backlog)
            partie.save()

            # Ajouter les joueurs à la partie
            for pseudo in pseudos:
                joueur = Joueur.objects.create(pseudo=pseudo)
                partie.joueurs.add(joueur)

        except IntegrityError:
            return JsonResponse({'error': 'Une erreur est survenue, veuillez réessayer.'}, status=500)

        # Rediriger vers la page affichant le code unique
        return render(request, 'code_partie.html', {'code_partie': code_unique})

    return render(request, 'lancer_partie.html')


from django.shortcuts import render, redirect

def rejoindre_partie(request):
    if request.method == 'POST':
        code_partie = request.POST.get('code_partie')
    
        if not code_partie:
            return render(request, 'rejoindre_partie.html', {'error': 'Code de la partie non spécifié'})

        try:
            # Récupérer la partie correspondant au code
            partie = Partie.objects.get(code=code_partie)
        except Partie.DoesNotExist:
            return render(request, 'rejoindre_partie.html', {'error': 'Partie non trouvée'})

        # Redirection vers l'URL de la partie
        return redirect('partie', code=code_partie)

    return render(request, 'rejoindre_partie.html')

def partie(request, code):
    try:
        partie = Partie.objects.get(code=code)
    except Partie.DoesNotExist:
        return JsonResponse({'error': 'Partie non trouvée'}, status=404)

    joueurs = partie.joueurs.all()
    tache_actuelle = partie.backlog[partie.active_task]
    mode = partie.mode  # Mode de jeu

    # Si le compteur 'tour_joueur' n'existe pas dans la session, on l'initialise
    if 'tour_joueur' not in request.session:
        request.session['tour_joueur'] = 0

    joueur_en_cours = joueurs[request.session['tour_joueur']]  # Joueur en cours

    if request.method == 'POST':
        # Récupérer le vote du joueur
        vote = request.POST.get('vote')

        # Enregistrer le vote dans la partie
        if partie.votes.get(partie.active_task) is None:
            partie.votes[partie.active_task] = {}

        partie.votes[partie.active_task][joueur_en_cours.id] = vote
        partie.save()

        # Passer au joueur suivant
        request.session['tour_joueur'] = (request.session['tour_joueur'] + 1) % len(joueurs)

        # Vérifier si tous les joueurs ont voté
        votes_actuels = partie.votes[partie.active_task]
        if len(votes_actuels) == len(joueurs):
            if len(set(votes_actuels.values())) == 1:  # Si tous les votes sont égaux
                # Passer à la tâche suivante
                partie.active_task += 1
                partie.save()

                # Réinitialiser les votes pour la tâche suivante
                partie.votes[partie.active_task] = {}
                partie.save()

                return redirect('partie', code=code)  # Recharger la page

        return redirect('partie', code=code)

    # Affichage des informations pour la partie
    return render(request, 'partie.html', {
        'partie': partie,
        'tache_actuelle': tache_actuelle['description'],
        'joueur_en_cours': joueur_en_cours,  # Le joueur dont c'est le tour
        'joueurs': joueurs,
        'mode': mode
    })


def soumettre_vote(request, code):
    partie = Partie.objects.get(code=code)
    joueurs = partie.joueurs.all()

    tache_actuelle = partie.backlog[partie.active_task]
    mode = partie.mode  # Mode de jeu

    # Enregistrer le vote du joueur
    vote = request.POST.get('vote')
    joueur_en_cours = joueurs[request.session['tour_joueur']]

    # Ajouter le vote à la liste des votes pour cette tâche
    if vote:
        if str(partie.active_task) not in partie.etat_avancement:
            partie.etat_avancement[str(partie.active_task)] = []

        partie.etat_avancement[str(partie.active_task)].append(vote)

    # Vérifier si tous les joueurs ont voté
    if len(partie.etat_avancement[str(partie.active_task)]) == len(joueurs):
        votes = partie.etat_avancement[str(partie.active_task)]

        if mode == 'strict':
            # Vérifier si tous les votes sont identiques
            if len(set(votes)) == 1:
                # Clôturer le vote pour cette tâche et passer à la suivante
                partie.active_task += 1  # Passer à la tâche suivante
                partie.etat_avancement[str(partie.active_task)] = []  # Réinitialiser les votes pour la tâche suivante
        elif mode == 'moyenne':
            # Calculer la moyenne des votes
            moyenne_vote = sum(int(vote) for vote in votes if vote.isdigit()) / len(votes)
            partie.etat_avancement[str(partie.active_task)] = moyenne_vote
            partie.active_task += 1  # Passer à la tâche suivante

        # Réinitialiser le tour du joueur après chaque tâche
        request.session['tour_joueur'] = 0

    else:
        # Incrémenter le tour pour passer au joueur suivant
        request.session['tour_joueur'] = (request.session['tour_joueur'] + 1) % len(joueurs)

    # Rediriger vers la page de la partie pour afficher le joueur suivant
    return redirect('partie', code=code)


