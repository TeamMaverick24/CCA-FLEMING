# Generated by Django 3.2.12 on 2024-05-29 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0006_alter_games_qr_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='games',
            name='qr_code',
            field=models.FileField(blank=True, default='', null=True, upload_to='qrcode'),
        ),
    ]
