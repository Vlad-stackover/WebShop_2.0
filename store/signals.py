from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models import F
from .models import Product

@receiver(pre_save, sender=Product)
def product_price_changed(sender, instance, **kwargs):
    if instance.pk:
        old_price = Product.objects.get(pk=instance.pk).price
        if instance.price != old_price:
            # Tutaj możesz zaimplementować logikę wysyłania powiadomienia o zmianie ceny
            print(f"Cena produktu {instance.name} została zmieniona z {old_price} na {instance.price}!")
