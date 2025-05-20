from django.contrib import admin
from .models import Product, Category, Review

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'rating', 'category')  # Shows these in list view
    search_fields = ('name',)
    list_filter = ('category',)
admin.site.register(Category)
admin.site.register(Review)
