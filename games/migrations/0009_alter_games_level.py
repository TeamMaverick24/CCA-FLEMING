# Generated by Django 3.2.12 on 2024-05-30 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0008_games_qr_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='games',
            name='level',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]