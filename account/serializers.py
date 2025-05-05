from rest_framework import serializers 
from .models import * 
from django.contrib.auth import get_user_model 
User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop('password', None)
        return ret


class RegisterSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = ('id', 'email', 'password', 'full_name', 'phone')
        extra_kwargs = { 'password': {'write_only':True}}
    
    def create(self, validated_data):
        # Check for unique email
        if User.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError({"email": "This email is already taken."})
        
        # Create user with hashed password
        user = User.objects.create_user(**validated_data)
        return user