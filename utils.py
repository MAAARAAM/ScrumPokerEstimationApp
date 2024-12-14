# utils.py

import json
from fonctionnalite import Fonctionnalite

def charger_backlog(filename):
    """Charge le backlog depuis un fichier JSON."""
    with open(filename, 'r') as file:
        return [Fonctionnalite(f['description']) for f in json.load(file)]

def sauvegarder_backlog(backlog, filename):
    """Sauvegarde l'état du backlog dans un fichier JSON."""
    with open(filename, 'w') as file:
        json.dump([{"description": f.description} for f in backlog], file)
