from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from django.conf import settings
from .coordinates import get_place_coordinates_by_address
from .models import Order
from backend.places.models import Place


@receiver(pre_save, sender=Order)
def pre_save_order(sender, instance, **kwargs):
    lat, lon = get_place_coordinates_by_address(settings.YANDEX_API_KEY, instance.address)
    place, created = Place.objects.get_or_create(address=instance.address, defaults={'lat': lat, 'lon': lon})
    if not created:
        place.updated_at = timezone.now()
        place.save()
