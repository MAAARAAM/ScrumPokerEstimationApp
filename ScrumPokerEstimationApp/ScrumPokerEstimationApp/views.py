"""
@file views.py
@brief Contient les vues de l'application Django pour gérer les parties et les joueurs.
"""

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

    """
    @brief Affiche la page d'accueil.
    @param request Objet HTTP contenant les informations de la requête.
    @return La page HTML de l'accueil.
    """

    return render(request, 'home.html')


def partie_suspendue(request, code):
    # Logique pour la vue partie_suspendue
    return render(request, 'partie_suspendue.html', {'code': code})


def generer_code_unique():

    """
    @brief Génère un code unique de 5 caractères (lettres et chiffres).
    @return Le code unique généré.
    """  

    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

def lancer_partie(request):

    """
    @brief Permet de lancer une nouvelle partie.
    @param request Objet HTTP contenant les informations de la requête.
    @return Une réponse JSON ou une redirection vers une page HTML selon le cas.
    """

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
    """
    @brief Permet à un joueur de rejoindre une partie existante.
    @param request Objet HTTP contenant les informations de la requête.
    @return Une redirection vers la partie ou un message d'erreur.
    """

    if request.method == 'POST':
        code_partie = request.POST.get('code_partie')
    
        if not code_partie:
            return render(request, 'rejoindre_partie.html', {'error': 'Code de la partie non spécifié'})

        try:
            # Récupérer la partie correspondant au code
            partie = Partie.objects.get(code=code_partie)
            
            # Vérifier si l'état de la partie est 'terminée'
            if partie.etat == 'terminee':
                return render(request, 'rejoindre_partie.html', {'error': 'Cette partie est déjà terminée'})
        except Partie.DoesNotExist:
            return render(request, 'rejoindre_partie.html', {'error': 'Partie non trouvée'})

        # Redirection vers l'URL de la partie
        return redirect('partie', code=code_partie)

    return render(request, 'rejoindre_partie.html')


def partie(request, code):
    """
    @brief Gère la logique d'une partie en cours.
    @param request Objet HTTP contenant les informations de la requête.
    @param code Le code unique de la partie.
    @return La page HTML de la partie avec les informations mises à jour.
    """

    try:
        partie = Partie.objects.get(code=code)
    except Partie.DoesNotExist:
        return JsonResponse({'error': 'Partie non trouvée'}, status=404)

    # Vérifiez si la partie est terminée
    if partie.etat == 'terminee':
        resultats = pretraiter_resultats(partie)
        return render(request, 'fin_partie.html', {
            'partie': partie,
            'mode': partie.mode,
            'resultats': resultats
        })

    joueurs = list(partie.joueurs.all())
    tache_actuelle_id = partie.active_task
    mode = partie.mode  # Mode de jeu

    # Initialiser l'état de la tâche actuelle si non défini
    if str(tache_actuelle_id) not in partie.etat_avancement:
        partie.etat_avancement[str(tache_actuelle_id)] = {
            'votes': [],  # Liste des votes par tour
            'tours': 0    # Compteur de tours
        }

    etat_tache = partie.etat_avancement[str(tache_actuelle_id)]
    tache_votes = etat_tache['votes']
    tours = etat_tache['tours']

    # Récupérer la tâche actuelle
    tache_actuelle = partie.backlog[tache_actuelle_id]

    # Initialiser ou récupérer le joueur en cours
    if 'tour_joueur' not in request.session:
        request.session['tour_joueur'] = 0

    joueur_en_cours = joueurs[request.session['tour_joueur']]

    if request.method == 'POST':
        vote = request.POST.get('vote')

        # Ajouter le vote au tour actuel
        if vote:
            if len(tache_votes) <= tours:
                tache_votes.append([])  # Créer un nouveau tour si nécessaire
            tache_votes[tours].append(vote)

        # Passer au joueur suivant
        request.session['tour_joueur'] = (request.session['tour_joueur'] + 1) % len(joueurs)

        # Si tous les joueurs ont voté pour ce tour
        if len(tache_votes[tours]) == len(joueurs):
            # Vérifier si tous les votes sont "Café"
            if all(vote == "Café" for vote in tache_votes[tours]):
                # Si tous les votes sont "Café", afficher le popup de suspension de la partie
                return render(request, 'partie_suspendue.html', {'partie': partie})

            if mode == 'strict':
                # Vérifier si tous les votes sont "?" et gérer le mode strict
                if all(v == "?" for v in tache_votes[tours]):
                    etat_tache['resultat'] = "Indécis"
                    partie.active_task += 1
                    if partie.active_task < len(partie.backlog):
                        partie.etat_avancement[str(partie.active_task)] = {'votes': [], 'tours': 0}
                    else:
                        partie.etat = 'terminee'
                        resultats = pretraiter_resultats(partie)
                        partie.save()
                        return render(request, 'fin_partie.html', {
                            'partie': partie,
                            'mode': mode,
                            'resultats': resultats
                        })
                else:
                    votes_effectifs = [v for v in tache_votes[tours] if v != "?"]
                    if len(set(votes_effectifs)) == 1:
                        # Unanimité atteinte
                        partie.active_task += 1
                        if partie.active_task < len(partie.backlog):
                            partie.etat_avancement[str(partie.active_task)] = {'votes': [], 'tours': 0}
                        else:
                            partie.etat = 'terminee'
                            resultats = pretraiter_resultats(partie)
                            partie.save()
                            return render(request, 'fin_partie.html', {
                                'partie': partie,
                                'mode': mode,
                                'resultats': resultats
                            })
                    else:
                        # Pas d'unanimité, démarrer un nouveau tour
                        etat_tache['tours'] += 1
                        request.session['tour_joueur'] = 0

            elif mode == 'moyenne':
                # Vérifier si c'est le premier tour et tous les joueurs n'ont pas voté de manière identique
                if tours == 0:  # Premier tour
                    if len(set(tache_votes[tours])) == 1:
                        # Unanimité atteinte
                        etat_tache['resultat'] = tache_votes[tours][0]  # Mettre le résultat du vote unique
                        partie.active_task += 1
                        if partie.active_task < len(partie.backlog):
                            partie.etat_avancement[str(partie.active_task)] = {'votes': [], 'tours': 0}
                        else:
                            partie.etat = 'terminee'
                            resultats = pretraiter_resultats(partie)
                            partie.save()
                            return render(request, 'fin_partie.html', {
                                'partie': partie,
                                'mode': mode,
                                'resultats': resultats
                            })
                    else:
                        # Pas d'unanimité, on passe à un tour de moyenne
                        etat_tache['tours'] += 1
                        request.session['tour_joueur'] = 0
                else:
                    # Calculer la moyenne des votes (exclure les "?")
                    votes_numeriques = [int(v) for v in tache_votes[tours] if v.isdigit()]
                    if votes_numeriques:
                        moyenne_vote = sum(votes_numeriques) / len(votes_numeriques)
                        etat_tache['moyenne'] = moyenne_vote

                    # Passer à la tâche suivante
                    partie.active_task += 1
                    if partie.active_task < len(partie.backlog):
                        partie.etat_avancement[str(partie.active_task)] = {'votes': [], 'tours': 0}
                    else:
                        partie.etat = 'terminee'
                        resultats = pretraiter_resultats(partie)
                        partie.save()
                        return render(request, 'fin_partie.html', {
                            'partie': partie,
                            'mode': mode,
                            'resultats': resultats
                        })

        partie.save()

        # Recharger la page pour le joueur suivant
        return redirect('partie', code=code)

    # Rendre la page de la partie
    return render(request, 'partie.html', {
        'partie': partie,
        'tache_actuelle': tache_actuelle['description'],
        'joueur_en_cours': joueur_en_cours,
        'joueurs': joueurs,
        'mode': mode,
        'votes': tache_votes,
        'tours': tours
    })


def pretraiter_resultats(partie):
    """
    @brief Prépare les résultats finaux pour une partie terminée.
    @param partie Instance de la classe Partie à traiter.
    @return Une liste des résultats des tâches.
    """
    resultats = []
    backlog = partie.backlog
    etat_avancement = partie.etat_avancement

    for tache_id, data in etat_avancement.items():
        tache_details = {
            'id': tache_id,
            'description': backlog[int(tache_id)]['description'],
            'votes': {idx: votes for idx, votes in enumerate(data['votes'])},
        }
        
        # Cas où tous les votes sont "?"
        if len(data['votes']) > 0 and all(v == "?" for v in data['votes'][-1]):
            tache_details['resultat'] = "Indécis"
        elif partie.mode == 'moyenne' and 'moyenne' in data:
            tache_details['resultat'] = f"Moyenne : {data['moyenne']:.2f}"
        elif partie.mode == 'strict' and len(data['votes']) > 0 and len(set(data['votes'][-1])) == 1:
            tache_details['resultat'] = f"Unanimité : {data['votes'][-1][0]}"
        else:
            tache_details['resultat'] = "Aucun consensus"
        
        resultats.append(tache_details)
    
    return resultats


def soumettre_vote(request, code):

    """
    @brief Permet aux joueurs de soumettre leurs votes pour une tâche.
    @param request Objet HTTP contenant les informations de la requête.
    @param code Le code unique de la partie.
    @return Une redirection vers la page de la partie après traitement du vote.
    """

    try:
        partie = Partie.objects.get(code=code)
    except Partie.DoesNotExist:
        return JsonResponse({'error': 'Partie non trouvée'}, status=404)

    joueurs = partie.joueurs.all()
    tache_actuelle = partie.backlog[partie.active_task]
    mode = partie.mode  # Mode de jeu

    # Enregistrer le vote du joueur
    vote = request.POST.get('vote')
    joueur_en_cours = joueurs[request.session['tour_joueur']]  # Le joueur en cours

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

    # Sauvegarder les changements dans la base de données
    partie.save()

    # Rediriger vers la page de la partie pour afficher le joueur suivant
    return redirect('partie', code=code)




