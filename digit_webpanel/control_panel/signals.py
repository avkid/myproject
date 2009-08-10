from django.db.models.signals import post_save, post_delete, pre_save
from control_panel.models import PriceLevel, PricePolicy, Discount, VolumeDiscount, SeasonDiscount

def update_has_levels(instance, **kwargs):
    # Update the denorm field on the corresponding PricePolicy object
    policy = instance.price_policy
    policy.has_levels = len(PriceLevel.objects.filter(price_policy=policy))
    policy.save()
    
post_save.connect(update_has_levels, sender=PriceLevel)
post_delete.connect(update_has_levels, sender=PriceLevel)


def update_discount_class(instance, **kwargs):
    # Update the discount class field
    instance.discount_class = instance.__class__.__name__

pre_save.connect(update_discount_class, sender=Discount)
pre_save.connect(update_discount_class, sender=VolumeDiscount)
pre_save.connect(update_discount_class, sender=SeasonDiscount)
