from rest_framework import serializers
from .models import Order
from .models import Product, Category, Review

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'user_email', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'user_email', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'product', 'product_name', 'product_image', 'amount',
            'total_price','quantity', 'address', 'payment_method', 'transaction_uuid',
            'payment_ref_id', 'is_paid', 'status', 'created_at'
        ]
        read_only_fields = ['user', 'transaction_uuid', 'payment_ref_id', 'is_paid', 'status', 'created_at' ,'quantity']