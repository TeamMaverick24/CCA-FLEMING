# Generated by Django 3.2.12 on 2024-04-06 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dh_user', '0002_alter_student_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
    ]