from collections import defaultdict
from django.db.models import Count, Q
from store.models import OrderItem
from recommendations.models import UserProductInteraction

class CollaborativeFiltering:
    def __init__(self):
        self.user_similarity_threshold = 0.3
        self.min_common_products = 2
        
    def recommend_for_user(self, user, n=5):
        """Enhanced collaborative filtering with interaction weights"""
        # Get current user's interactions with weights
        user_interactions = UserProductInteraction.objects.filter(
            user=user
        ).values_list('product_id', 'weight')
        
        if not user_interactions:
            return []
            
        user_products = {pid: weight for pid, weight in user_interactions}
        
        # Find similar users with weighted Jaccard similarity
        similar_users = self._find_similar_users(user, user_products.keys())
        
        if not similar_users:
            return []
            
        # Get top products from similar users with weighted scores
        recommendations = defaultdict(float)
        for similar_user in similar_users:
            interactions = UserProductInteraction.objects.filter(
                user_id=similar_user
            ).exclude(product_id__in=user_products.keys())
            
            for interaction in interactions:
                recommendations[interaction.product_id] += interaction.weight
        
        # Sort by weighted score and get top n
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return [pid for pid, score in sorted_recs[:n]]
    
    def _find_similar_users(self, target_user, target_products):
        """Find users with weighted Jaccard similarity"""
        # Get all users who interacted with any target product
        similar_users = defaultdict(lambda: {'common': set(), 'total': set()})
        
        for product_id in target_products:
            interactions = UserProductInteraction.objects.filter(
                product_id=product_id
            ).exclude(user=target_user)
            
            for interaction in interactions:
                user_id = interaction.user_id
                similar_users[user_id]['common'].add(product_id)
                similar_users[user_id]['total'].add(product_id)
        
        # Calculate weighted Jaccard similarity
        similar_users = {
            user_id: len(data['common']) / (
                len(target_products) + len(data['total']) - len(data['common'])
            )
            for user_id, data in similar_users.items()
            if len(data['common']) >= self.min_common_products
        }
        
        # Filter by threshold
        return [
            user_id for user_id, score in similar_users.items()
            if score >= self.user_similarity_threshold
        ]