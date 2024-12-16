# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # This will map the root URL to the home view
    path('lancer_partie/', views.lancer_partie, name='lancer_partie'),
    path('rejoindre_partie/', views.rejoindre_partie, name='rejoindre_partie'),
    path('demarrer_voting/<str:code_partie>/', views.demarrer_voting, name='demarrer_voting'),
    path('partie/', views.partie, name='partie'), 
]


