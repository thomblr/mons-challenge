# Generated by Django 3.1.6 on 2021-02-04 17:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_savetrippoints'),
    ]

    operations = [
        migrations.AddField(
            model_name='savetrippoints',
            name='statut',
            field=models.CharField(choices=[('validated', 'Validé'), ('waiting', 'En attente'), ('refused', 'Refusé')], default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
    ]
