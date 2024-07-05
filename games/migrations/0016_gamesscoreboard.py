# Generated by Django 3.2.12 on 2024-06-30 13:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('games', '0015_alter_gameuser_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='GamesScoreBoard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_games', models.CharField(blank=True, max_length=250, null=True)),
                ('success_games', models.CharField(blank=True, max_length=250, null=True)),
                ('game_level', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='games.gamestype')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]