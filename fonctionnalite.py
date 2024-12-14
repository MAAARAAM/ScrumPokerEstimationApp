# Définir les modes de jeu
mode_strict = 'strict'
mode_moyenne = 'moyenne'
mode_mediane = 'mediane'
mode_majorite_absolue = 'majorite_absolue'
mode_majorite_relative = 'majorite_relative'

class Fonctionnalite:
    def __init__(self, description, tache=None):
        self.description = description
        self.tache = tache  # Nouvelle propriété pour stocker la tâche concernée
        self.estime = None

    def estimer(self, votes, mode):
        """Estime la fonctionnalité en fonction du mode de jeu."""
        if mode == mode_strict:
            if len(set(votes)) == 1:  # Unanimité
                self.estime = votes[0]
        elif mode == mode_moyenne:
            self.estime = sum(votes) / len(votes)
        elif mode == mode_mediane:
            self.estime = sorted(votes)[len(votes) // 2]
        elif mode == mode_majorite_absolue:
            self.estime = max(set(votes), key=votes.count)
        elif mode == mode_majorite_relative:
            self.estime = max(set(votes), key=lambda x: votes.count(x))
