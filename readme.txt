ScrumPokerEstimationApp
Prérequis
Avant de démarrer l'application en local, assurez-vous d'avoir installé les outils suivants sur votre machine :

Python (version 3.8 ou supérieure)
Pip (gestionnaire de paquets Python)
Django (version 5.1.4 ou supérieure)

Étapes pour exécuter l'application en local :
1. Clonez ou téléchargez le projet
Si vous utilisez Git, clonez le dépôt :
git clone https://github.com/MAAARAAM/ScrumPokerEstimationApp.git
cd ScrumPokerEstimationApp
2. Créez un environnement virtuel
Il est recommandé d'utiliser un environnement virtuel pour isoler les dépendances du projet :
python -m venv venv
3. Activez l'environnement virtuel
Sous Windows :
.\venv\Scripts\activate
Sous macOS/Linux :
source venv/bin/activate
4. Appliquez les migrations de base de données
Avant de lancer le serveur, vous devez appliquer les migrations pour configurer la base de données :
python manage.py migrate
5. Lancez le serveur de développement
Démarrez l'application en local :
python manage.py runserver
6. Accédez à l'application
Ouvrez votre navigateur et allez à l'URL suivante :
http://127.0.0.1:8000/

L'application devrait maintenant être en cours d'exécution en local.

Requirements
Les bibliothèques nécessaires pour le projet sont listées ci-dessous. 
Django == 5.1.4
pytest == 8.3.4
pytest-django == 4.9.0

1.Installer pytest
Pour exécuter les tests unitaires, vous devez d'abord installer pytest en utilisant la commande suivante :
pip install pytest pytest-django
2.Lancer les tests unitaires
Une fois pytest installé, vous pouvez exécuter les tests unitaires de l'application avec la commande suivante :
pytest
Cela exécutera tous les tests présents dans le répertoire de test et affichera les résultats dans la console.


Pour manipuler la base de données SQLite3 utilisée par Django, installez DB Browser for SQLite (disponible sur le site officiel ou via Homebrew/apt-get). Ouvrez le fichier db.sqlite3 dans l'outil pour explorer, modifier ou exécuter des requêtes SQL sur les tables. Vous pouvez aussi utiliser le shell Django avec la commande python manage.py dbshell pour exécuter des requêtes SQL directement dans le terminal. Pour gérer les migrations, utilisez python manage.py makemigrations pour créer des migrations et python manage.py migrate pour les appliquer.

