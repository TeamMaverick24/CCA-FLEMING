# Generated by Django 3.2.12 on 2024-05-30 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0009_alter_games_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='games',
            name='qr_value',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
