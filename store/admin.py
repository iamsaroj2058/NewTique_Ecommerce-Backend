from django.contrib import admin
from .models import Product, Category, Review
from .models import Order

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'rating', 'category')  # Shows these in list view
    search_fields = ('name',)
    list_filter = ('category',)
admin.site.register(Category)
admin.site.register(Review)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "amount", "is_paid", "created_at")
    list_filter = ("is_paid",)
    search_fields = ("user__email", "product__title")