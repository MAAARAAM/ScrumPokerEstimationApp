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

        # Récupérer les pseudos des joueurs et les afficher
        joueurs = partie.joueurs.all()
        
        # Si des joueurs existent dans la partie, on peut afficher leur liste
        if joueurs.exists():
            joueurs_pseudos = [joueur.pseudo for joueur in joueurs]
            card_values = [0, 1, 2, 3, 5, 8, 13, 20, 40, 100]  # Liste des valeurs des cartes
            return render(request, 'partie.html', {
                'partie': partie, 
                'joueurs_pseudos': joueurs_pseudos,
                'card_values': card_values  # Passer la liste de cartes
            })

        else:
            return render(request, 'rejoindre_partie.html', {'error': 'Aucun joueur dans cette partie.'})

    return render(request, 'rejoindre_partie.html')

def partie(request, code):
    try:
        partie = Partie.objects.get(code=code)
    except Partie.DoesNotExist:
        return JsonResponse({'error': 'Partie non trouvée'}, status=404)
    
    # Assurez-vous que active_task est un index dans le backlog
    if partie.active_task < len(partie.backlog):
        tache_actuelle = partie.backlog[partie.active_task]
        tache_description = tache_actuelle['description']
    else:
        tache_description = "Aucune tâche actuelle"
    
    if request.method == 'POST':
        pseudo = request.POST['pseudo']
        try:
            joueur = Joueur.objects.get(pseudo=pseudo)
        except Joueur.DoesNotExist:
            return JsonResponse({'error': 'Joueur non trouvé'}, status=404)

        joueur.vote = request.POST['vote']
        joueur.save()

        # Vérifiez si tous les joueurs ont voté
        if all(joueur.vote for joueur in partie.joueurs.all()):
            votes = [int(joueur.vote) for joueur in partie.joueurs.all()]
            if partie.mode == 'strict':
                # Si tous les votes sont identiques, on applique le vote à la tâche
                if len(set(votes)) == 1:
                    partie.etat_avancement[str(partie.active_task)] = votes[0]
                    partie.active_task += 1
            elif partie.mode == 'moyenne':
                # Calcul de la moyenne des votes
                partie.etat_avancement[str(partie.active_task)] = sum(votes) / len(votes)
                partie.active_task += 1

            # Vérification si le backlog est terminé
            if partie.active_task == len(partie.backlog):
                # Sauvegarder le résultat dans un fichier
                with open('resultat.json', 'w') as f:
                    json.dump(partie.etat_avancement, f)
                return JsonResponse({'message': 'Backlog terminé !'})

            # Réinitialiser les votes des joueurs pour la tâche suivante
            for joueur in partie.joueurs.all():
                joueur.vote = None
                joueur.save()

    return render(request, 'partie.html', {'partie': partie, 'tache_actuelle': tache_description})

