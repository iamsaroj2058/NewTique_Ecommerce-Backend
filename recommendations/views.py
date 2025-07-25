from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from store.models import Product
from .services import RecommendationService
from .serializers import UserInteractionSerializer, RecommendationResponseSerializer
from store.serializers import ProductSerializer
import logging

logger = logging.getLogger(__name__)

class RecommendationView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        try:
            # Validate parameters
            product_id = request.query_params.get("product_id")
            n = min(max(1, int(request.query_params.get("n", 5))), 5)  # Force 1-5
            
            product = None
            if product_id:
                product = Product.objects.get(id=product_id)

            # Get recommendations
            service = RecommendationService()
            products = service.get_recommendations(request.user, product, n)
            
            # Final verification
            if products.count() > n:
                logger.error(f"Recommendation overflow: {products.count()} > {n}")
                products = products[:n]
            
            # Prepare response
            return Response({
                "success": True,
                "count": products.count(),
                "recommendations": ProductSerializer(
                    products,
                    many=True,
                    context={'request': request}
                ).data
            })
            
        except Product.DoesNotExist:
            return Response(
                {"success": False, "error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Recommendation error: {e}")
            return Response(
                {"success": False, "error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserInteractionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UserInteractionSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        interactions = request.user.userproductinteraction_set.all()
        serializer = UserInteractionSerializer(interactions, many=True)
        return Response(serializer.data)
