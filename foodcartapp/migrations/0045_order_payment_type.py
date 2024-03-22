# Generated by Django 3.2.15 on 2024-03-22 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_auto_20240322_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_type',
            field=models.CharField(choices=[('cash', 'Наличные'), ('card', 'Картой онлайн')], default='card', max_length=10, verbose_name='Тип оплаты'),
        ),
    ]
