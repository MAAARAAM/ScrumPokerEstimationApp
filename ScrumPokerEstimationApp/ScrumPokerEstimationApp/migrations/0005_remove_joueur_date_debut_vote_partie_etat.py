# Generated by Django 5.1.4 on 2024-12-20 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ScrumPokerEstimationApp', '0004_joueur_date_debut_vote'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='joueur',
            name='date_debut_vote',
        ),
        migrations.AddField(
            model_name='partie',
            name='etat',
            field=models.CharField(choices=[('en_cours', 'En cours'), ('terminee', 'Terminée'), ('annulee', 'Annulée')], default='en_cours', help_text="L'état actuel de la partie", max_length=20),
        ),
    ]
