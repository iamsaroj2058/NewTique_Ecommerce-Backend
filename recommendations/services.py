from django.db.models import QuerySet, Count, Case, When, Subquery, OuterRef
from store.models import Product, OrderItem
from .algorithms.collaborative import CollaborativeFiltering
from .algorithms.content_based import ContentBasedRecommender
from .models import ProductSimilarity
import logging

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self):
        self.collaborative_filter = CollaborativeFiltering()
        self.content_based_filter = ContentBasedRecommender()
        self._initialize_models()

    def _initialize_models(self):
        try:
            if not ProductSimilarity.objects.exists():
                logger.info("Initializing recommendation models...")
                self.content_based_filter.train()
                self._store_similarities()
        except Exception as e:
            logger.error(f"Model initialization error: {e}")

    def _store_similarities(self):
        """Store only significant similarities"""
        for i, product_id in enumerate(self.content_based_filter.product_ids):
            similarities = self.content_based_filter.similarities[i]
            product = Product.objects.get(id=product_id)
            
            significant_similarities = [
                (j, score) for j, score in enumerate(similarities)
                if j != i and score > 0.1
            ][:20]  # Top 20 similar products
            
            ProductSimilarity.objects.bulk_create([
                ProductSimilarity(
                    product=product,
                    similar_product_id=self.content_based_filter.product_ids[j],
                    similarity_score=score
                ) for j, score in significant_similarities
            ])

    def get_recommendations(self, user, product=None, n: int = 5) -> QuerySet:
        """STRICTLY returns exactly 'n' recommended products"""
        n = min(max(1, n), 5)  # Force between 1-5
        
        # Step 1: Get strict recommendations
        recommended_ids = self._get_recommendation_ids(user, product, n)
        
        # Step 2: If insufficient, get fallbacks
        if not recommended_ids or len(recommended_ids) < n:
            fallback_ids = self._get_fallback_ids(user, product, n - len(recommended_ids))
            recommended_ids = list(set(recommended_ids + fallback_ids))[:n]
        
        # Step 3: Final fetch with strict enforcement
        return self._get_products_by_ids(recommended_ids)

    def _get_recommendation_ids(self, user, product, n):
        """Returns only IDs of recommended products"""
        ids = set()
        
        # Content-based
        if product:
            try:
                cb_ids = list(ProductSimilarity.objects
                    .filter(product=product)
                    .order_by('-similarity_score')
                    .values_list('similar_product_id', flat=True)[:n])
                ids.update(cb_ids)
            except Exception as e:
                logger.error(f"Content-based error: {e}")

        # Collaborative
        if user.is_authenticated:
            try:
                cf_ids = self.collaborative_filter.recommend_for_user(user, n)
                ids.update(cf_ids)
            except Exception as e:
                logger.error(f"Collaborative error: {e}")

        return list(ids)[:n]

    def _get_fallback_ids(self, user, product, needed):
        """Fallback that strictly limits results"""
        base_qs = Product.objects
        
        # Same category fallback
        if product and product.category:
            return list(base_qs.filter(category=product.category)
                .exclude(id=product.id)
                .order_by('-rating')
                .values_list('id', flat=True)[:needed])
        
        # User's categories fallback
        if user.is_authenticated:
            user_cats = OrderItem.objects.filter(
                order__user=user
            ).values_list('product__category', flat=True).distinct()
            
            if user_cats:
                return list(base_qs.filter(category__in=user_cats)
                    .order_by('-rating')
                    .values_list('id', flat=True)[:needed])
        
        # Global popular fallback
        return list(base_qs.annotate(
                order_count=Count('orderitem')
            ).order_by('-order_count', '-rating')
            .values_list('id', flat=True)[:needed])

    def _get_products_by_ids(self, ids):
        """Final product fetch with order preservation"""
        if not ids:
            return Product.objects.none()
            
        order_case = Case(*[When(id=id, then=pos) for pos, id in enumerate(ids)])
        return Product.objects.filter(id__in=ids).order_by(order_case)