from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from account.api.views import *

router = DefaultRouter()
router.register('register', RegisterViewset, basename='register')
router.register('login', LoginViewset, basename='login')
router.register('users', UserViewset, basename='users')

# First collect all router-generated URLs
urlpatterns = router.urls

# Then extend with custom URL(s)
urlpatterns += [
    path('verify-token/', VerifyTokenView.as_view(), name='verify-token'),
]