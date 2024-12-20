"""
@file models.py
@brief Définit les modèles de données pour les joueurs et les parties dans l'application Django.
"""

from django.db import models

class Joueur(models.Model):
    """
    @class Joueur
    @brief Représente un joueur dans une partie.
    @var pseudo Le pseudo unique du joueur.
    @var vote Le vote actuel du joueur (optionnel).
    """
    pseudo = models.CharField(max_length=100)
    vote = models.CharField(max_length=20, blank=True, null=True)

class Partie(models.Model):
    """
    @class Partie
    @brief Représente une partie avec ses joueurs, son backlog, et son état d'avancement.
    @var code Le code unique de la partie.
    @var mode Le mode de jeu (strict ou moyenne).
    @var backlog La liste des tâches de la partie.
    @var active_task L'index de la tâche actuelle.
    @var etat_avancement Les résultats des votes par tâche.
    @var joueurs Les joueurs associés à cette partie.
    @var votes Les votes des joueurs pour chaque tâche.
    @var etat L'état actuel de la partie (par défaut 'en_cours').
    """
    code = models.CharField(max_length=10, unique=True)
    mode = models.CharField(max_length=10, choices=[('strict', 'Strict'), ('moyenne', 'Moyenne')])
    backlog = models.JSONField()
    active_task = models.IntegerField(default=0)
    etat_avancement = models.JSONField(default=dict)
    joueurs = models.ManyToManyField(Joueur)
    votes = models.JSONField(default=dict)
    etat = models.CharField(
        max_length=20,
        default='en_cours',
        choices=[
            ('en_cours', 'En cours'),
            ('terminee', 'Terminée'),
            ('annulee', 'Annulée')
        ],
        help_text="L'état actuel de la partie"
    )

    def save(self, *args, **kwargs):
        """
        @brief Enregistre l'état de la partie tout en initialisant les votes pour chaque tâche du backlog.
        """
        if not self.backlog:
            self.backlog = []
        for tache in self.backlog:
            if 'votes' not in tache:
                tache['votes'] = []
        super(Partie, self).save(*args, **kwargs)
