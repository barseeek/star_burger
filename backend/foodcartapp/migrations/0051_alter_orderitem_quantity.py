# Generated by Django 3.2.15 on 2024-03-30 15:55

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_auto_20240324_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество'),
        ),
    ]