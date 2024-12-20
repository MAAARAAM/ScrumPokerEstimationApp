# Generated by Django 5.1.4 on 2024-12-16 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Joueur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pseudo', models.CharField(max_length=100)),
                ('vote', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Partie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('mode', models.CharField(choices=[('strict', 'Mode Strict'), ('moyenne', 'Mode Moyenne')], max_length=20)),
                ('backlog', models.JSONField()),
                ('etat_avancement', models.JSONField(default=dict)),
                ('active_task', models.IntegerField(default=0)),
                ('joueurs', models.ManyToManyField(related_name='parties', to='ScrumPokerEstimationApp.joueur')),
            ],
        ),
    ]
