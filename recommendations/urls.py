from django.urls import path
from .views import RecommendationView, UserInteractionView

urlpatterns = [
    path('', RecommendationView.as_view(), name='recommendations'),
    path('interactions/', UserInteractionView.as_view(), name='user-interactions'),
]