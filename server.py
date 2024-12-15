from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)
PARTIES_FILE = 'parties.json'
STATE_FILE = 'state.json'

# Vérifier si le fichier existe, sinon le créer
if not os.path.exists(PARTIES_FILE):
    with open(PARTIES_FILE, 'w') as f:
        json.dump([], f)

if not os.path.exists(STATE_FILE):
    with open(STATE_FILE, 'w') as f:
        json.dump({}, f)  # Initialisez avec un dictionnaire vide

# Route pour récupérer toutes les parties
@app.route('/parties', methods=['GET'])
def get_parties():
    with open(PARTIES_FILE, 'r') as f:
        parties = json.load(f)
    return jsonify(parties)

# Route pour récupérer une partie spécifique par code
@app.route('/parties/<code>', methods=['GET'])
def get_partie(code):
    with open(PARTIES_FILE, 'r') as f:
        parties = json.load(f)
    for partie in parties:
        if partie['code'] == code:
            return jsonify(partie)
    return jsonify({'error': 'Partie non trouvée'}), 404

# Route pour ajouter une nouvelle partie
@app.route('/parties', methods=['POST'])
def add_partie():
    nouvelle_partie = request.json
    if not nouvelle_partie:
        return jsonify({'error': 'Données manquantes'}), 400

    with open(PARTIES_FILE, 'r') as f:
        parties = json.load(f)

    parties.append(nouvelle_partie)

    with open(PARTIES_FILE, 'w') as f:
        json.dump(parties, f, indent=4)

    return jsonify({'message': 'Partie ajoutée avec succès'}), 201

# Route pour mettre à jour une partie existante
@app.route('/parties/<code>', methods=['PUT'])
def update_partie(code):
    update_data = request.json
    if not update_data:
        return jsonify({'error': 'Données manquantes'}), 400

    with open(PARTIES_FILE, 'r') as f:
        parties = json.load(f)

    for partie in parties:
        if partie['code'] == code:
            partie.update(update_data)
            with open(PARTIES_FILE, 'w') as f:
                json.dump(parties, f, indent=4)
            return jsonify({'message': 'Partie mise à jour avec succès'})

    return jsonify({'error': 'Partie non trouvée'}), 404

# Route pour supprimer une partie
@app.route('/parties/<code>', methods=['DELETE'])
def delete_partie(code):
    with open(PARTIES_FILE, 'r') as f:
        parties = json.load(f)

    parties = [partie for partie in parties if partie['code'] != code]

    with open(PARTIES_FILE, 'w') as f:
        json.dump(parties, f, indent=4)

    return jsonify({'message': 'Partie supprimée avec succès'})

# Route pour récupérer l'état
@app.route('/state', methods=['GET'])
def get_state():
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        state = {}  # Réinitialisez avec un état vide si le fichier est invalide
    return jsonify(state)


# Route pour mettre à jour l'état
@app.route('/state', methods=['PUT'])
def update_state():
    new_state = request.json
    if not new_state:
        return jsonify({'error': 'Données manquantes'}), 400

    with open(STATE_FILE, 'r') as f:
        state = json.load(f)

    state.update(new_state)  # Met à jour les données

    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

    return jsonify({'message': 'État mis à jour avec succès'})

# Route pour réinitialiser l'état
@app.route('/state/reset', methods=['POST'])
def reset_state():
    with open(STATE_FILE, 'w') as f:
        json.dump({}, f)  # Réinitialisez avec un dictionnaire vide
    return jsonify({'message': 'État réinitialisé avec succès'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
