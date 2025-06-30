from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import Review, OrderItem
from .models import UserProductInteraction

@receiver(post_save, sender=Review)
def track_review(sender, instance, created, **kwargs):
    if created:
        UserProductInteraction.objects.create(
            user=instance.user,
            product=instance.product,
            interaction_type='review',
            weight=1.5  # Higher weight for reviews
        )

@receiver(post_save, sender=OrderItem)
def track_purchase(sender, instance, created, **kwargs):
    if created:
        UserProductInteraction.objects.create(
            user=instance.order.user,
            product=instance.product,
            interaction_type='purchase',
            weight=2.0  # Highest weight for purchases
        )