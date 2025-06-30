from collections import defaultdict
from django.db.models import Count
from store.models import OrderItem

class CollaborativeFiltering:
    def __init__(self):
        self.user_similarity_threshold = 0.5
        
    def recommend_for_user(self, user, n=5):
        """Recommend products based on similar users' preferences"""
        # Get current user's purchased products
        user_products = set(
            OrderItem.objects.filter(order__user=user)
            .values_list('product_id', flat=True)
        )
        
        # Find similar users (who bought similar products)
        similar_users = self._find_similar_users(user, user_products)
        
        # Get top products from similar users
        recommendations = (
            OrderItem.objects.filter(order__user__in=similar_users)
            .exclude(product_id__in=user_products)
            .values('product')
            .annotate(count=Count('product'))
            .order_by('-count')[:n]
        )
        
        return [item['product'] for item in recommendations]
    
    def _find_similar_users(self, target_user, target_products):
        """Find users with similar purchase history"""
        if not target_products:
            return []
            
        # Get users who bought any of the target products
        similar_users = defaultdict(int)
        for product_id in target_products:
            users = OrderItem.objects.filter(
                product_id=product_id
            ).exclude(order__user=target_user).values_list('order__user', flat=True)
            
            for user_id in users:
                similar_users[user_id] += 1
                
        # Normalize scores and filter by threshold
        max_count = max(similar_users.values()) if similar_users else 1
        return [
            user_id for user_id, count in similar_users.items()
            if count / max_count >= self.user_similarity_threshold
        ]