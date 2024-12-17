from django.db import models

class Joueur(models.Model):
    pseudo = models.CharField(max_length=100)
    vote = models.CharField(max_length=20, blank=True, null=True)

class Partie(models.Model):
    code = models.CharField(max_length=5, unique=True)
    mode = models.CharField(max_length=10)  # strict ou moyenne
    backlog = models.JSONField()
    joueurs = models.ManyToManyField('Joueur', blank=True)
    active_task = models.IntegerField(default=0)
    etat_avancement = models.JSONField(default=dict)  

