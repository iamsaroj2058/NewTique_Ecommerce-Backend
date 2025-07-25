from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from store.models import Product
import numpy as np

class ContentBasedRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.similarities = None
        self.product_ids = None
        
    def train(self):
        """Precompute product similarities with enhanced features"""
        products = Product.objects.prefetch_related('category').all()
        
        # Create enhanced feature strings
        product_features = [
            self._create_feature_string(p) for p in products
        ]
        
        # Create TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(product_features)
        
        # Compute cosine similarities with smoothing
        self.similarities = cosine_similarity(tfidf_matrix)
        self.similarities = np.nan_to_num(self.similarities, nan=0.0)
        self.product_ids = [p.id for p in products]
        
    def _create_feature_string(self, product):
        """Create enhanced feature string for product"""
        features = [
            product.name,
            product.category.name if product.category else '',
            product.description,
            ' '.join([t.name for t in product.tags.all()]),
            ' '.join([str(a.value) for a in product.attributes.all()])
        ]
        return ' '.join(filter(None, features))
        
    def recommend_for_product(self, product_id, n=5):
        """Get similar products based on content"""
        try:
            idx = self.product_ids.index(product_id)
            sim_scores = list(enumerate(self.similarities[idx]))
            
            # Sort by score, exclude self, and filter by minimum similarity
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = [
                (i, score) for i, score in sim_scores 
                if i != idx and score > 0.1  # Minimum similarity threshold
            ][:n]
            
            return [self.product_ids[i] for i, _ in sim_scores]
        except (ValueError, AttributeError):
            return []