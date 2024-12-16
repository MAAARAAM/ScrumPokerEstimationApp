from django.db import models

class Joueur(models.Model):
    pseudo = models.CharField(max_length=100)
    vote = models.CharField(max_length=20, blank=True, null=True)

class Partie(models.Model):
    code = models.CharField(max_length=50, unique=True)
    mode = models.CharField(max_length=20, choices=[
        ('strict', 'Mode Strict'),
        ('moyenne', 'Mode Moyenne')
    ])
    backlog = models.JSONField()
    etat_avancement = models.JSONField(default=dict)
    joueurs = models.ManyToManyField(Joueur, related_name="parties")
    active_task = models.IntegerField(default=0)
