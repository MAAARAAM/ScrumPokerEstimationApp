from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Partie, Joueur, Fonctionnalite
import random
# views.py
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')  # You can create a template for this page

def lancer_partie(request):
    if request.method == 'POST':
        joueurs = []
        nb_joueurs = int(request.POST['nb_joueurs'])
        for i in range(nb_joueurs):
            pseudo = request.POST.get(f'joueur_{i+1}')
            joueur = Joueur(pseudo=pseudo)
            joueur.save()
            joueurs.append(joueur)

        tache = request.POST['tache']
        mode = request.POST['mode']
        partie = Partie.objects.create(mode=mode, tache=tache)
        partie.joueurs.add(*joueurs)

        # Générer un code unique
        code = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
        partie.code = code
        partie.save()

        return JsonResponse({'message': f'La partie a été lancée ! Code de la partie : {code}'})

    return render(request, 'lancer_partie.html')

def rejoindre_partie(request):
    if request.method == 'POST':
        code_partie = request.POST['code_partie']
        try:
            partie = Partie.objects.get(code=code_partie)
            pseudo = request.POST['pseudo']
            joueur = Joueur.objects.create(pseudo=pseudo)
            partie.joueurs.add(joueur)

            return JsonResponse({'message': f"Vous avez rejoint la partie : {partie.code}"})
        except Partie.DoesNotExist:
            return JsonResponse({'message': 'Code de partie invalide, essayez encore.'})

    return render(request, 'rejoindre_partie.html')

def demarrer_voting(request, code_partie):
    try:
        partie = Partie.objects.get(code=code_partie)
        partie.demarrer_voting()
        return JsonResponse({'message': f"Le vote a commencé pour la tâche: {partie.tache}"})
    except Partie.DoesNotExist:
        return JsonResponse({'message': 'Partie non trouvée.'})
