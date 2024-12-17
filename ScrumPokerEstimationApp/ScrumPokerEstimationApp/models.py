from django.db import models

class Joueur(models.Model):
    pseudo = models.CharField(max_length=50, unique=True)
    vote = models.CharField(max_length=10, null=True, blank=True)  # Valeur du vote du joueur

class Partie(models.Model):
    code = models.CharField(max_length=10, unique=True)
    mode = models.CharField(max_length=10, choices=[('strict', 'Strict'), ('moyenne', 'Moyenne')])
    backlog = models.JSONField()  # Liste des tâches
    active_task = models.IntegerField(default=0)  # Index de la tâche actuelle
    etat_avancement = models.JSONField(default=dict)  # Résultats des votes par tâche
    joueurs = models.ManyToManyField(Joueur)
