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
        # Récupérer le mode de la partie
        mode = request.POST.get('mode')
        if not mode:
            return JsonResponse({'error': 'Le mode de jeu doit être sélectionné.'}, status=400)

        # Récupérer les tâches du backlog
        backlog = []
        for key, value in request.POST.items():
            if key.startswith('task_') and value.strip():
                backlog.append({
                    "id": str(uuid.uuid4()),
                    "description": value.strip(),
                    "date_created": timezone.now().isoformat()
                })

        if not backlog:
            return JsonResponse({'error': 'Veuillez décrire au moins une tâche.'}, status=400)

        # Générer un code unique pour la partie
        code_unique = generer_code_unique()
        while Partie.objects.filter(code=code_unique).exists():
            code_unique = generer_code_unique()

        # Créer la partie avec le backlog
        try:
            partie = Partie.objects.create(code=code_unique, mode=mode, backlog=backlog)
            partie.save()
        except IntegrityError:
            return JsonResponse({'error': 'Une erreur est survenue, veuillez réessayer.'}, status=500)

        # Rediriger vers la page affichant le code unique
        return render(request, 'code_partie.html', {'code_partie': code_unique})

    # Afficher le formulaire pour lancer la partie
    return render(request, 'lancer_partie.html')


def rejoindre_partie(request):
    if request.method == 'POST':
        code_partie = request.POST['code_partie']
        pseudo = request.POST['pseudo']

        try:
            # Récupérer la partie correspondant au code
            partie = Partie.objects.get(code=code_partie)
        except Partie.DoesNotExist:
            return render(request, 'rejoindre_partie.html', {'error': 'Partie non trouvée'})

        # Ajouter le joueur à la partie
        try:
            joueur = Joueur.objects.create(pseudo=pseudo)
            partie.joueurs.add(joueur)
            partie.save()
        except Exception as e:
            return render(request, 'rejoindre_partie.html', {'error': f'Erreur : {str(e)}'})

        # Rediriger vers la page de la partie
        return redirect('partie', code=partie.code)

    # Afficher le formulaire pour rejoindre la partie
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
