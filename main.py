import json
from joueur import Joueur
from partie import Partie 
from fonctionnalite import Fonctionnalite
from config import mode_strict, mode_moyenne, mode_mediane, mode_majorite_absolue, mode_majorite_relative

# Fonction pour charger le backlog depuis un fichier JSON
def charger_backlog(filename):
    """Charge le backlog depuis un fichier JSON."""
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            # Vérifier que chaque élément a bien les clés 'description' et 'tache'
            return [Fonctionnalite(f.get('description', ''), f.get('tache', '')) for f in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fonction pour sauvegarder le backlog dans un fichier JSON
def sauvegarder_backlog(backlog, filename):
    """Sauvegarde l'état du backlog dans un fichier JSON."""
    with open(filename, 'w') as file:
        # Sauvegarde sous forme de dictionnaires avec 'description' et 'tache'
        json.dump([{"description": f.description, "tache": f.tache} for f in backlog], file, indent=4)

# Fonction pour lancer une nouvelle partie
def lancer_partie():
    """Permet de lancer une nouvelle partie."""
    joueurs = []
    nb_joueurs = int(input("Combien de joueurs ? "))
    for _ in range(nb_joueurs):
        pseudo = input("Entrez le pseudo du joueur : ")
        joueurs.append(Joueur(pseudo))

    # Demander à l'utilisateur de saisir la tâche
    tache = input("Décrivez la tâche concernée par cette partie : ")

    # Ajouter la tâche au backlog
    backlog = charger_backlog('backlog.json')
    fonctionnalite = Fonctionnalite(description=f"Tâche liée à la partie : {tache}", tache=tache)
    backlog.append(fonctionnalite)
    sauvegarder_backlog(backlog, 'backlog.json')

    print("Choisissez le mode de jeu :")
    print("1. Mode strict (Unanimité)")
    print("2. Moyenne")
    print("3. Médiane")
    print("4. Majorité absolue")
    print("5. Majorité relative")
    mode_choisi = int(input())

    # Choisir le mode de jeu
    mode = None
    if mode_choisi == 1:
        mode = mode_strict
    elif mode_choisi == 2:
        mode = mode_moyenne
    elif mode_choisi == 3:
        mode = mode_mediane
    elif mode_choisi == 4:
        mode = mode_majorite_absolue
    elif mode_choisi == 5:
        mode = mode_majorite_relative
    else:
        print("Mode non valide")
        return

    # Crée la partie avec la tâche et les autres paramètres
    partie = Partie(joueurs, backlog, mode, tache)

    # Sauvegarder la partie en cours avec un code unique
    partie.sauvegarder()
    print(f"La partie a été lancée ! Code de la partie : {partie.code}")
    
    # Retourner au menu principal après la création de la partie
    menu()

# Fonction pour rejoindre une partie
def rejoindre_partie():
    """Permet de rejoindre une partie existante."""
    code_partie = input("Entrez le code de la partie : ")
    # Recherche la partie dans le fichier parties.json
    with open('parties.json', 'r') as file:
        parties = json.load(file)
    for partie in parties:
        if partie["code"] == code_partie:
            print(f"Vous avez rejoint la partie : {partie['code']}")
            # Une fois que la partie est trouvée, démarrer le vote
            joueurs = [Joueur(j['pseudo']) for j in partie["joueurs"]]
            backlog = charger_backlog('backlog.json')
            tache = partie["tache"]
            mode = partie["mode"]
            nouvelle_partie = Partie(joueurs, backlog, mode, tache)
            nouvelle_partie.demarrer_voting()
            return
    print("Code de partie invalide, essayez encore.")

# Menu principal
def menu():
    """Affiche le menu principal."""
    print("1. Lancer une nouvelle partie")
    print("2. Rejoindre une partie")
    choix = input("Choisissez une option (1 ou 2) : ")

    if choix == "1":
        lancer_partie()
    elif choix == "2":
        rejoindre_partie()
    else:
        print("Choix invalide. Réessayez.")
        menu()

# Lancer le menu principal
menu()
