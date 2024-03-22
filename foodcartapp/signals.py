from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order


@receiver(pre_save, sender=Order)
def update_order_status(sender, instance, **kwargs):
    if instance.cook and instance.status != Order.OrderStatus.COOKING:
        instance.status = Order.OrderStatus.COOKING
