from rest_framework import serializers
from store.models import Product
from store.serializers import ProductSerializer
from .models import UserProductInteraction

class UserInteractionSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True,many=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    
    class Meta:
        model = UserProductInteraction
        fields = [
            'id',
            'user',
            'product',
            'product_id',
            'interaction_type',
            'weight',
            'created_at'
        ]
        read_only_fields = ['user', 'created_at']

class RecommendationResponseSerializer(serializers.Serializer):
    recommendations = ProductSerializer(many=True)
    algorithm = serializers.CharField()
    count = serializers.IntegerField()

