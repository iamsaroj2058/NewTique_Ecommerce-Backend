from django.db.models import QuerySet
from store.models import Product
from .algorithms.collaborative import CollaborativeFiltering
from .algorithms.content_based import ContentBasedRecommender


class RecommendationService:
    def __init__(self):
        """Initialize recommendation services with trained models"""
        self.collaborative_filter = CollaborativeFiltering()
        self.content_based_filter = ContentBasedRecommender()
        self._initialize_models()

    def _initialize_models(self):
        """Initialize and train recommendation models"""
        try:
            self.content_based_filter.train()
        except Exception as e:
            # Log this error in production
            print(f"Error training content-based model: {e}")
            # Fallback to untrained model
            self.content_based_filter = ContentBasedRecommender()

    def get_recommendations(self, user, product=None, n: int = 5) -> QuerySet:
        """
        Get hybrid recommendations combining collaborative and content-based filtering
        
        Args:
            user: The user to get recommendations for
            product: Optional product to get similar items for
            n: Number of recommendations to return
            
        Returns:
            QuerySet of recommended products
        """
        recommendations = set()
        
        # Collaborative filtering (user-based)
        if user.is_authenticated:
            try:
                cf_recs = self.collaborative_filter.recommend_for_user(user, n)
                recommendations.update(cf_recs)
            except Exception as e:
                print(f"Collaborative filtering failed: {e}")

        # Content-based filtering (item-based)
        if product:
            try:
                cb_recs = self.content_based_filter.recommend_for_product(product.id, n)
                recommendations.update(cb_recs)
            except Exception as e:
                print(f"Content-based filtering failed: {e}")

        # Fallback to popular products if no recommendations
        if not recommendations:
            return self._get_popular_products(n)
        
        return self._get_filtered_products(recommendations, n)

    def _get_popular_products(self, n: int) -> QuerySet:
        """Fallback to popular products when no recommendations available"""
        return Product.objects.order_by('-rating')[:n]

    def _get_filtered_products(self, product_ids: set, n: int) -> QuerySet:
        """Get product queryset from set of IDs"""
        return Product.objects.filter(id__in=list(product_ids)[:n])