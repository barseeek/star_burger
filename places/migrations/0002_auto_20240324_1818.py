# Generated by Django 3.2.15 on 2024-03-24 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='lat',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Широта'),
        ),
        migrations.AlterField(
            model_name='place',
            name='lon',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Долгота'),
        ),
    ]
