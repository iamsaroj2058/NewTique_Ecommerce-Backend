from rest_framework import serializers
from django.db.models import Avg, Count
from .models import Product, Category, Review, Order, OrderItem

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        extra_fields = ['reviews_count', 'average_rating']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['reviews_count'] = instance.reviews.count()
        representation['average_rating'] = instance.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        return representation

class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'user_email', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'user_email', 'user_name', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    subtotal = serializers.SerializerMethodField()  # This requires get_subtotal() method
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_image', 
            'quantity', 'price', 'subtotal'
        ]
    
    # This method MUST be properly indented (outside Meta class)
    def get_subtotal(self, obj):
        """Calculate subtotal (quantity × price)"""
        return obj.quantity * obj.product.price

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_email', 'items', 'total_price', 'address',
            'payment_method', 'transaction_uuid', 'payment_ref_id', 'is_paid',
            'status', 'created_at'
        ]
        read_only_fields = [
            'user', 'transaction_uuid', 'payment_ref_id', 'is_paid',
            'status', 'created_at', 'total_price'
        ]

    def create(self, validated_data):
        # This will be handled by your view, but included for completeness
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            
        return order