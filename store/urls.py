from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ReviewViewSet, EsewaInitiatePaymentView,EsewaPaymentSuccessView,CashOnDeliveryView,OrderViewSet,get_product_stocks

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'orders', OrderViewSet, basename='orders') 


urlpatterns = [
    path('', include(router.urls)),
    path('esewa/initiate/', EsewaInitiatePaymentView.as_view(), name='esewa-initiate'),
    path('esewa-initiate-payment/', EsewaInitiatePaymentView.as_view()),
    path('esewa-payment-success/', EsewaPaymentSuccessView.as_view()),
    path('cash-on-delivery/', CashOnDeliveryView.as_view(), name='cash-on-delivery'),
    path('api/products/stocks/', get_product_stocks, name='product-stocks'),
]
