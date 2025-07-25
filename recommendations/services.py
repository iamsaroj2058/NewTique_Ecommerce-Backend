from django.db.models import QuerySet, Count, Q, Case, When
from store.models import Product, OrderItem
from .algorithms.collaborative import CollaborativeFiltering
from .algorithms.content_based import ContentBasedRecommender
from .models import ProductSimilarity
import logging

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self):
        """Initialize recommendation services with trained models"""
        self.collaborative_filter = CollaborativeFiltering()
        self.content_based_filter = ContentBasedRecommender()
        self._initialize_models()

    def _initialize_models(self):
        """Initialize and train recommendation models"""
        try:
            if not ProductSimilarity.objects.exists():
                logger.info("Training content-based model...")
                self.content_based_filter.train()
                self._store_similarities()
        except Exception as e:
            logger.error(f"Error initializing models: {e}")

    def _store_similarities(self):
        """Store computed similarities in database"""
        for i, product_id in enumerate(self.content_based_filter.product_ids):
            similarities = self.content_based_filter.similarities[i]
            product = Product.objects.get(id=product_id)
            
            # Get top 20 similar products
            sim_scores = list(enumerate(similarities))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:21]  # Exclude self and get top 20
            
            # Bulk create similarities
            ProductSimilarity.objects.bulk_create([
                ProductSimilarity(
                    product=product,
                    similar_product_id=self.content_based_filter.product_ids[j],
                    similarity_score=score
                )
                for j, score in sim_scores if score > 0.1  # Threshold
            ])

    def get_recommendations(self, user, product=None, n: int = 5) -> QuerySet:
        """
        Get properly filtered recommendations
        Returns: Product queryset with ONLY recommended products
        """
        n = max(1, min(n, 20))  # Ensure reasonable limits
        
        # Get recommendation IDs from both systems
        recommended_ids = self._get_recommendation_ids(user, product, n)
        
        if not recommended_ids:
            return self._get_fallback_products(user, product, n)
            
        # Get ONLY the recommended products in correct order
        return self._get_ordered_products(recommended_ids, n)

    def _get_recommendation_ids(self, user, product, n):
        """Combine recommendations from both systems"""
        recommended_ids = set()
        
        # Content-based recommendations
        if product:
            try:
                cb_ids = self._get_content_based_recs(product.id, n)
                recommended_ids.update(cb_ids)
            except Exception as e:
                logger.error(f"Content-based error: {e}")

        # Collaborative recommendations
        if user.is_authenticated:
            try:
                cf_ids = self.collaborative_filter.recommend_for_user(user, n)
                recommended_ids.update(cf_ids)
            except Exception as e:
                logger.error(f"Collaborative error: {e}")

        return recommended_ids

    def _get_content_based_recs(self, product_id, n):
        """Get content-based recommendations with fallback"""
        # Try database first
        recs = ProductSimilarity.objects.filter(
            product_id=product_id,
            similarity_score__gt=0.1
        ).order_by('-similarity_score').values_list('similar_product_id', flat=True)[:n]
        
        return recs or self.content_based_filter.recommend_for_product(product_id, n)

    def _get_ordered_products(self, product_ids, n):
        """Get products while preserving recommendation order"""
        if not product_ids:
            return Product.objects.none()
            
        # Create case to preserve the original recommendation order
        order_case = Case(*[
            When(id=id, then=pos) for pos, id in enumerate(product_ids)
        ])
        
        return (
            Product.objects
            .filter(id__in=product_ids)
            .order_by(order_case)
            .prefetch_related('images')[:n]  # Optimize for product images
        )

    def _get_fallback_products(self, user, product, n):
        """Fallback recommendation strategy"""
        # Use the correct related_name (orderitem instead of order_items)
        fallback_qs = Product.objects.annotate(
            order_count=Count('orderitem')  # Changed from 'order_items' to 'orderitem'
        ).order_by('-order_count', '-rating')
        
        if product and product.category:
            # Same category fallback
            return fallback_qs.filter(
                category=product.category
            ).exclude(id=product.id)[:n]
        
        if user.is_authenticated:
            # User's preferred categories fallback
            user_cats = OrderItem.objects.filter(
                order__user=user
            ).values_list('product__category', flat=True).distinct()
            
            if user_cats:
                return fallback_qs.filter(
                    category__in=user_cats
                )[:n]
        
        # Global popular products fallback
        return fallback_qs[:n]