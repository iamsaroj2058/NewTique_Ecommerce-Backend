from .collaborative import CollaborativeFiltering
from .content_based import ContentBasedRecommender

class HybridRecommender:
    def __init__(self):
        self.cf = CollaborativeFiltering()
        self.cb = ContentBasedRecommender()
        
    def recommend(self, user, product=None, n=5):
        cf_recs = self.cf.recommend_for_user(user, n) if user.is_authenticated else []
        cb_recs = self.cb.recommend_for_product(product.id, n) if product else []
        return list(set(cf_recs + cb_recs))[:n]