from django.contrib import admin
from .models import Product, Category, Review, Order, OrderItem  # Add OrderItem to imports
from .models import Cart, CartItem

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'rating', 'category')
    search_fields = ('name',)
    list_filter = ('category',)

admin.site.register(Category)
admin.site.register(Review)

# Add this inline class to show order items within the Order admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # No extra empty forms
    readonly_fields = ('product', 'quantity', 'price')  # Make fields read-only
    can_delete = False  # Prevent deletion through admin

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "display_products", "total_price", "payment_method", "is_paid", "status", "created_at")
    list_filter = ("is_paid", "status", "payment_method", "created_at")
    search_fields = ("user__email", "transaction_uuid")
    readonly_fields = ("transaction_uuid", "created_at")
    inlines = [OrderItemInline]  # Add the inline
    
    # Custom method to display products in list view
    def display_products(self, obj):
        return ", ".join([item.product.name for item in obj.items.all()])
    display_products.short_description = 'Products'

# Register OrderItem if you want a separate admin view
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('product',)
    search_fields = ('order__transaction_uuid', 'product__name')


admin.site.register(Cart)
admin.site.register(CartItem)