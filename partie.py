from config import mode_strict, mode_moyenne, mode_mediane, mode_majorite_absolue, mode_majorite_relative
import json, random, string

class Partie:

    def __init__(self, joueurs, backlog, mode, tache):
        self.joueurs = joueurs
        self.backlog = backlog
        self.mode = mode
        self.tache = tache
        self.code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))  # Générer un code unique
        self.etat = "en cours"  # Etat de la partie
        self.votes = []  # Liste pour stocker les votes des joueurs
        self.cartes_poker = [0, 1, 2, 3, 5, 8, 13, 20, 40, 100, "Café", "?"]  # Liste Fibonacci modifiée

    def sauvegarder(self):
        """Sauvegarde la partie dans un fichier JSON."""
        partie_data = {
            "code": self.code,
            "etat": self.etat,
            "mode": self.mode,
            "nb_joueurs": len(self.joueurs),
            "tache": self.tache,
            "joueurs": [{"pseudo": joueur.pseudo} for joueur in self.joueurs],  # Ajout des joueurs
        }
        try:
            with open('parties.json', 'r') as file:
                parties = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            parties = []

        parties.append(partie_data)
        with open('parties.json', 'w') as file:
            json.dump(parties, file, indent=4)

    def demarrer_voting(self, tour=1):
        """Démarre le processus de vote pour la tâche."""
        print(f"Recommencer le vote pour : {self.tache} (Tour {tour})")
        self.votes = []  # Réinitialiser la liste des votes

        # Demander à chaque joueur de choisir un vote
        for joueur in self.joueurs:
            while True:
                print("Choisissez une carte de vote parmi les suivantes : ")
                for i, carte in enumerate(self.cartes_poker, 1):
                    print(f"{i}. {carte}")
                try:
                    choix = int(input(f"{joueur.pseudo}, entrez le numéro de votre carte de vote pour la tâche '{self.tache}': "))
                    if 1 <= choix <= len(self.cartes_poker):
                        vote = self.cartes_poker[choix - 1]  # Récupérer la carte choisie
                        self.votes.append(vote)  # Ajouter le vote du joueur
                        break  # Sortir de la boucle après un vote valide
                    else:
                        print("Numéro invalide, veuillez choisir une carte valide.")
                except ValueError:
                    print("Veuillez entrer un nombre valide.")

        print(f"Votes : {self.votes}")
        self.estimer(tour)

    def estimer(self, tour=1):
        """Estime la fonctionnalité selon le mode de jeu, avec respect des règles pour chaque mode."""
        print(f"Estimation en cours (tour {tour})...")

        # Compter les occurrences des votes
        votes_comptes = {vote: self.votes.count(vote) for vote in set(self.votes)}

        # Gérer le vote "Café"
        if "Café" in votes_comptes and votes_comptes["Café"] > len(self.joueurs) / 2:
            print("Une pause a été demandée par la majorité. Prise en compte de la demande : Café.")
            return

        # Premier tour : Unanimité exigée pour tous les modes
        if tour == 1 or self.mode == mode_strict:
            if len(set(self.votes)) == 1:
                print(f"L'estimation pour '{self.tache}' est : {self.votes[0]}")
                self.valider(self.votes[0])
                return
            else:
                print("Les votes ne sont pas unanimes. Discutez et recommencez le vote.")
                self.demarrer_voting(tour + 1)  # Recommencer le vote
                return

        # Tours suivants : Estimation selon le mode
        votes_numeriques = [vote for vote in self.votes if isinstance(vote, (int, float))]
        estimation = None

        if self.mode == mode_moyenne:
            if votes_numeriques:
                estimation = sum(votes_numeriques) / len(votes_numeriques)
                print(f"L'estimation pour '{self.tache}' (moyenne) est : {estimation:.2f}")
        elif self.mode == mode_mediane:
            if votes_numeriques:
                sorted_votes = sorted(votes_numeriques)
                mid = len(sorted_votes) // 2
                estimation = sorted_votes[mid] if len(sorted_votes) % 2 != 0 else \
                    (sorted_votes[mid - 1] + sorted_votes[mid]) / 2
                print(f"L'estimation pour '{self.tache}' (médiane) est : {estimation}")
        elif self.mode == mode_majorite_absolue:
            estimation = None
            for vote, count in votes_comptes.items():
                if count > len(self.joueurs) / 2:
                    estimation = vote
                    break
            if estimation:
                print(f"L'estimation pour '{self.tache}' (majorité absolue) est : {estimation}")
            else:
                print("Pas de majorité absolue. Discutez et recommencez le vote.")
                self.demarrer_voting(tour + 1)
                return
        elif self.mode == mode_majorite_relative:
            estimation = max(votes_comptes, key=votes_comptes.get)
            print(f"L'estimation pour '{self.tache}' (majorité relative) est : {estimation}")

        # Validation après estimation
        if estimation is not None:
            self.valider(estimation)

    def valider(self, estimation):
        """Valide la fonctionnalité après estimation."""
        if estimation == "Café":
            print("Une pause a été validée.")
        else:
            print(f"La tâche '{self.tache}' a été validée avec une estimation de {estimation}.")



