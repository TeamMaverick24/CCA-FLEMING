# Generated by Django 3.2.12 on 2024-07-03 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dh_user', '0008_alter_student_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]