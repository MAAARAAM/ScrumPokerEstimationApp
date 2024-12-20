from django.urls import path
from .views import home, lancer_partie, partie, rejoindre_partie, partie_suspendue

urlpatterns = [
    # Chemins d'accès
    path('', home, name='home'),
    path('lancer_partie/', lancer_partie, name='lancer_partie'),
    path('partie/<str:code>/', partie, name='partie'),
    path('rejoindre_partie/', rejoindre_partie, name='rejoindre_partie'),
    path('partie/<str:code>/suspendue/', partie_suspendue, name='partie_suspendue')
]
