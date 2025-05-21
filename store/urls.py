from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ReviewViewSet, EsewaInitiatePaymentView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'reviews', ReviewViewSet, basename='reviews')

urlpatterns = [
    path('', include(router.urls)),
    path('esewa/initiate/', EsewaInitiatePaymentView.as_view(), name='esewa-initiate'),
]
