# joueur.py

import random

class Joueur:
    def __init__(self, pseudo):
        self.pseudo = pseudo
        self.vote = None

    def choisir_carte(self):
        """Permet à un joueur de choisir une carte."""
        cartes = [1, 2, 3, 5, 8, 13, 'café']
        self.vote = random.choice(cartes)
