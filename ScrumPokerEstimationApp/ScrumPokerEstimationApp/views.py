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
        # Récupération du nombre de joueurs
        try:
            nb_joueurs = int(request.POST['nb_joueurs'])
        except (KeyError, ValueError):
            return JsonResponse({'error': 'Le nombre de joueurs est invalide.'}, status=400)

        # Récupérer les pseudos des joueurs
        pseudos = [request.POST.get(f'joueur_{i+1}', '').strip() for i in range(nb_joueurs)]

        # Vérification des pseudos
        if '' in pseudos:
            return JsonResponse({'error': 'Tous les pseudos des joueurs doivent être fournis.'}, status=400)
        if len(pseudos) != len(set(pseudos)):
            return JsonResponse({'error': 'Les pseudos des joueurs doivent être uniques.'}, status=400)

        # Récupérer le mode de la partie
        mode = request.POST.get('mode')
        if not mode:
            return JsonResponse({'error': 'Le mode de jeu doit être sélectionné.'}, status=400)

        # Récupérer la description de la tâche unique
        task_description = request.POST.get('task_1', '').strip()
        if not task_description:
            return JsonResponse({'error': 'Veuillez décrire la tâche à estimer.'}, status=400)

        # Créer le backlog avec une seule tâche
        backlog = [
            {
                "id": str(uuid.uuid4()),  # Identifiant unique pour la tâche
                "description": task_description,
                "date_created": timezone.now().isoformat()
            }
        ]

        # Générer un code unique pour la partie
        code_unique = generer_code_unique()
        while Partie.objects.filter(code=code_unique).exists():
            code_unique = generer_code_unique()  # Assurez-vous que le code est unique

        # Créer les joueurs
        joueurs = []
        try:
            for pseudo in pseudos:
                joueur = Joueur.objects.create(pseudo=pseudo)
                joueurs.append(joueur)
        except Exception as e:
            return JsonResponse({'error': f'Erreur lors de la création des joueurs : {str(e)}'}, status=500)

        # Créer la partie avec le backlog et les joueurs
        try:
            partie = Partie.objects.create(code=code_unique, mode=mode, backlog=backlog)
            partie.joueurs.set(joueurs)
            partie.save()
        except IntegrityError:
            return JsonResponse({'error': 'Une erreur est survenue, veuillez réessayer.'}, status=500)

        # Afficher le code unique pour permettre aux joueurs de rejoindre la partie
        return render(request, 'code_partie.html', {'code_partie': code_unique})

    # Afficher le formulaire pour lancer la partie
    return render(request, 'lancer_partie.html')


def rejoindre_partie(request):
    if request.method == 'POST':
        code_partie = request.POST['code_partie']
        pseudo = request.POST['pseudo']

        try:
            partie = Partie.objects.get(code=code_partie)
        except Partie.DoesNotExist:
            return render(request, 'rejoindre_partie.html', {'error': 'Partie non trouvée'})

        if len(partie.joueurs.all()) < partie.mode:  # Vérifier si la partie a encore des places
            joueur = Joueur.objects.create(pseudo=pseudo)
            partie.joueurs.add(joueur)
            partie.save()
            return redirect('partie', code=partie.code)
        else:
            return render(request, 'rejoindre_partie.html', {'error': 'La partie est pleine'})

    return render(request, 'rejoindre_partie.html')

def partie(request, code):
    partie = Partie.objects.get(code=code)
    
    # Assurez-vous que active_task est un index dans le backlog
    if partie.active_task < len(partie.backlog):
        tache_actuelle = partie.backlog[partie.active_task]
        tache_description = tache_actuelle['description']
    else:
        tache_description = "Aucune tâche actuelle"
    
    if request.method == 'POST':
        joueur = Joueur.objects.get(pseudo=request.POST['pseudo'])
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

