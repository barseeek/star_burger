from django.db import models
from django.utils import timezone


class Place(models.Model):
    address = models.CharField(max_length=255, verbose_name='Адрес', unique=True)
    lat = models.DecimalField(decimal_places=6, max_digits=10, verbose_name='Широта',
                              null=True, blank=True)
    lon = models.DecimalField(decimal_places=6, max_digits=10, verbose_name='Долгота',
                              null=True, blank=True)
    updated_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания', blank=True)

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'

    def __str__(self):
        return self.address
