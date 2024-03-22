# Generated by Django 3.2.15 on 2024-03-22 08:35

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_order_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivered_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата доставки'),
        ),
        migrations.AddField(
            model_name='order',
            name='processed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата звонка'),
        ),
    ]
