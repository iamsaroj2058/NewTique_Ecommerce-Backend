from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    ReviewViewSet,
    OrderViewSet,
    EsewaInitiatePaymentView,
    EsewaPaymentSuccessView,
    CashOnDeliveryView,
    get_product_stocks,
    CartViewSet,
)

# Register viewsets with DRF router
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'orders', OrderViewSet, basename='orders')

# Define cart view actions explicitly
cart_list_view = CartViewSet.as_view({'get': 'list'})
cart_add_view = CartViewSet.as_view({'post': 'add_item'})
cart_update_view = CartViewSet.as_view({'post': 'update_quantity'})
cart_remove_view = CartViewSet.as_view({'delete': 'remove_item'})

urlpatterns = [
    # API router-based endpoints
    path('', include(router.urls)),

    # Payment URLs
    path('esewa/initiate/', EsewaInitiatePaymentView.as_view(), name='esewa-initiate'),
    path('esewa/initiate-payment/', EsewaInitiatePaymentView.as_view(), name='esewa-initiate-duplicate'),  # optional: remove one
    path('esewa/payment-success/', EsewaPaymentSuccessView.as_view(), name='esewa-payment-success'),
    path('cash-on-delivery/', CashOnDeliveryView.as_view(), name='cash-on-delivery'),

    # Stock check endpoint
    path('products/stocks/', get_product_stocks, name='product-stocks'),

    # Cart API endpoints
    path('cart/', cart_list_view, name='cart-list'),
    path('cart/add/', cart_add_view, name='cart-add'),
    path('cart/update/', cart_update_view, name='cart-update'),
    path('cart/remove/', cart_remove_view, name='cart-remove'),
]
