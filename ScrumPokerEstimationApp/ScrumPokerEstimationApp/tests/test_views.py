import pytest
from django.urls import reverse
from ScrumPokerEstimationApp.models import Partie
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.django_db
def test_home(client):
    response = client.get(reverse('home'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_lancer_partie(client):
    data = {
        'mode': 'strict',
        'nb_joueurs': 3,
        'player_1': 'Alice',
        'player_2': 'Bob',
        'player_3': 'Charlie',
        'nb_taches': 2,
        'tache_1': 'Task 1',
        'tache_2': 'Task 2',
    }
    response = client.post(reverse('lancer_partie'), data)
    assert response.status_code == 200
    assert Partie.objects.count() == 1
    partie = Partie.objects.first()
    assert partie.joueurs.count() == 3

@pytest.mark.django_db
def test_rejoindre_partie(client):
    partie = Partie.objects.create(code='ABCDE', mode='strict', backlog=[])
    response = client.post(reverse('rejoindre_partie'), {'code_partie': 'ABCDE'})
    assert response.status_code == 302  # Redirection
    assert response.url == reverse('partie', args=['ABCDE'])
