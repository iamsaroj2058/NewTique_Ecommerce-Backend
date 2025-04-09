from django.shortcuts import render
from store.serializers import ProductSerializer
# Create your views here.
from rest_framework import viewsets
from .models import Product


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
