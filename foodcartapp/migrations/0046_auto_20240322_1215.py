# Generated by Django 3.2.15 on 2024-03-22 09:15

import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_order_payment_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivered_at',
            field=models.DateTimeField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Дата создания'))], verbose_name='Дата доставки'),
        ),
        migrations.AlterField(
            model_name='order',
            name='processed_at',
            field=models.DateTimeField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Дата создания'))], verbose_name='Дата звонка'),
        ),
    ]