from django.db import models
import random
import string

# Définir les modes de jeu en tant que constantes
MODE_CHOICES = [
    ('strict', 'Unanimité'),
    ('moyenne', 'Moyenne'),
    ('mediane', 'Médiane'),
    ('majorite_absolue', 'Majorité absolue'),
    ('majorite_relative', 'Majorité relative')
]

class Fonctionnalite(models.Model):
    description = models.CharField(max_length=255)
    tache = models.CharField(max_length=255, blank=True, null=True)
    estime = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.description

    def estimer(self, votes, mode):
        if mode == 'strict' and len(set(votes)) == 1:
            self.estime = votes[0]
        elif mode == 'moyenne':
            self.estime = sum(votes) / len(votes)
        elif mode == 'mediane':
            self.estime = sorted(votes)[len(votes) // 2]
        elif mode == 'majorite_absolue':
            self.estime = max(set(votes), key=votes.count)
        elif mode == 'majorite_relative':
            self.estime = max(set(votes), key=lambda x: votes.count(x))
        self.save()

class Joueur(models.Model):
    pseudo = models.CharField(max_length=255)
    vote = models.CharField(max_length=10, blank=True, null=True)

    def choisir_carte(self):
        cartes = [1, 2, 3, 5, 8, 13, 'Café']
        self.vote = random.choice(cartes)
        self.save()

class Partie(models.Model):
    code = models.CharField(max_length=6, unique=True)
    etat = models.CharField(max_length=20, default='en cours')
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    tache = models.CharField(max_length=255)
    joueurs = models.ManyToManyField(Joueur)
    votes = models.JSONField(default=list)

    def __str__(self):
        return f"Partie {self.code} - {self.tache}"

    def demarrer_voting(self):
        # Logique de vote
        for joueur in self.joueurs.all():
            joueur.choisir_carte()
            self.votes.append(joueur.vote)
        self.save()

    def estimer(self):
        # Exemple d'estimation, selon le mode choisi
        if self.mode == 'moyenne':
            self.estime = sum([vote for vote in self.votes if isinstance(vote, int)]) / len(self.votes)
        self.save()
