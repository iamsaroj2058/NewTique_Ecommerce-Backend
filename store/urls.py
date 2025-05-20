from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, get_esewa_payment_data, verify_esewa_payment

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')

urlpatterns = [
    path('', include(router.urls)),
    path('esewa/initiate/', get_esewa_payment_data, name='esewa_initiate'),
    path('esewa/verify/', verify_esewa_payment, name='esewa_verify'),
]
