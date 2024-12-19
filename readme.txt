README for ScrumPokerEstimationApp
Prérequis
Avant de démarrer l'application en local, assurez-vous d'avoir installé les outils suivants sur votre machine :

Python (version 3.8 ou supérieure)
Pip (gestionnaire de paquets Python)
Django (version 5.1.4 ou supérieure)

Étapes pour exécuter l'application en local
Clonez ou téléchargez le projet
Si vous utilisez Git, clonez le dépôt :
git clone <URL_DE_VOTRE_DEPOT>
cd ScrumPokerEstimationApp
Créez un environnement virtuel
Il est recommandé d'utiliser un environnement virtuel pour isoler les dépendances du projet :

python -m venv venv
Activez l'environnement virtuel
Sous Windows :
.\venv\Scripts\activate
Sous macOS/Linux :
source venv/bin/activate
Installez les dépendances
Installez les dépendances nécessaires avec pip :

pip install -r requirements.txt

Appliquez les migrations de base de données
Avant de lancer le serveur, vous devez appliquer les migrations pour configurer la base de données :
python manage.py migrate
Lancez le serveur de développement
Démarrez l'application en local :
python manage.py runserver
Accédez à l'application
Ouvrez votre navigateur et allez à l'URL suivante :
http://127.0.0.1:8000/
L'application devrait maintenant être en cours d'exécution en local.

requirements
Django==5.1.4
pytest==8.3.4
pytest-django==4.9.0
