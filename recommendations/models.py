from django.db import models
from django.conf import settings
from store.models import Product

class UserProductInteraction(models.Model):
    """Tracks user interactions with products"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    interaction_type = models.CharField(
        max_length=20,
        choices=[
            ('view', 'View'),
            ('cart', 'Added to Cart'),
            ('purchase', 'Purchased'),
            ('review', 'Reviewed')
        ]
    )
    weight = models.FloatField(default=1.0)  # Importance of this interaction
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product', 'interaction_type')

class ProductSimilarity(models.Model):
    """Stores precomputed product similarities for content-based filtering"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='similarities')
    similar_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='similar_to')
    similarity_score = models.FloatField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'similar_product')