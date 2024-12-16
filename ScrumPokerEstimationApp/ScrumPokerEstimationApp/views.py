import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.db import IntegrityError
from .models import Partie, Joueur
import uuid

def home(request):
    return render(request, 'home.html')

def lancer_partie(request):
    if request.method == 'POST':
        nb_joueurs = int(request.POST['nb_joueurs'])
        pseudos = [request.POST[f'joueur_{i+1}'] for i in range(nb_joueurs)]

        # Vérifier que les pseudos sont uniques
        if len(pseudos) != len(set(pseudos)):
            return JsonResponse({'error': 'Les pseudos des joueurs doivent être uniques.'}, status=400)

        mode = request.POST['mode']

        # Récupérer la description de la tâche unique
        task_description = request.POST.get('task_1')  # Une seule tâche
        if not task_description:
            return JsonResponse({'error': 'Veuillez décrire la tâche à estimer.'}, status=400)

        # Créer le backlog avec la seule tâche
        backlog = [
            {
                "id": str(uuid.uuid4()),  # Identifiant unique pour la tâche
                "description": task_description,
                "date_created": timezone.now().isoformat()  # Date de création
            }
        ]

        # Créer les joueurs
        joueurs = [Joueur.objects.create(pseudo=pseudo) for pseudo in pseudos]

        # Créer la partie avec le backlog
        partie = Partie.objects.create(code="12345", mode=mode, backlog=backlog)
        partie.joueurs.set(joueurs)
        partie.save()

        return redirect('partie', code=partie.code)

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

