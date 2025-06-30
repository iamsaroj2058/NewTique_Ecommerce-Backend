from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from store.models import Product
from .services import RecommendationService
from .serializers import (
    UserInteractionSerializer,
    RecommendationResponseSerializer
)

class RecommendationView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        product_id = request.query_params.get('product_id')
        n = int(request.query_params.get('n', 5))
        
        product = None
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        service = RecommendationService()
        recommendations = service.get_recommendations(
            request.user,
            product=product,
            n=n
        )
        
        response_data = {
            'recommendations': recommendations,
            'algorithm': 'hybrid',
            'count': len(recommendations)
        }
        
        serializer = RecommendationResponseSerializer(response_data)
        return Response(serializer.data)

class UserInteractionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = UserInteractionSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        interactions = request.user.userproductinteraction_set.all()
        serializer = UserInteractionSerializer(interactions, many=True)
        return Response(serializer.data)