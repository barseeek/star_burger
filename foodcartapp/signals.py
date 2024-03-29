from django.db.models import Sum
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from requests import HTTPError

from star_burger import settings
from .coordinates import fetch_coordinates, get_place_coordinates_by_address
from .models import Order, OrderItem
from places.models import Place


@receiver(pre_save, sender=Order)
def pre_save_order(sender, instance, **kwargs):
    try:
        place = Place.objects.get(address=instance.address)
    except Place.DoesNotExist:
        place = None
    if place:
        place.updated_at = timezone.now()
    else:
        get_place_coordinates_by_address(settings.YANDEX_API_KEY, instance.address)

