from django.contrib import admin
from .models import UserProductInteraction, ProductSimilarity

@admin.register(UserProductInteraction)
class UserProductInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'interaction_type', 'weight', 'created_at')
    list_filter = ('interaction_type', 'created_at')
    search_fields = ('user__email', 'product__name')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'product')

@admin.register(ProductSimilarity)
class ProductSimilarityAdmin(admin.ModelAdmin):
    list_display = ('product', 'similar_product', 'similarity_score', 'last_updated')
    search_fields = ('product__name', 'similar_product__name')
    list_filter = ('last_updated',)
    raw_id_fields = ('product', 'similar_product')