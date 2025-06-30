from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from store.models import Product

class ContentBasedRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
    def train(self):
        """Precompute product similarities"""
        products = Product.objects.all()
        product_descriptions = [
            f"{p.name} {p.category.name} {p.description}" 
            for p in products
        ]
        
        # Create TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(product_descriptions)
        
        # Compute cosine similarities
        self.similarities = cosine_similarity(tfidf_matrix)
        self.product_ids = [p.id for p in products]
        
    def recommend_for_product(self, product_id, n=5):
        """Get similar products based on content"""
        try:
            idx = self.product_ids.index(product_id)
            sim_scores = list(enumerate(self.similarities[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:n+1]  # Exclude self and get top n
            
            return [self.product_ids[i] for i, _ in sim_scores]
        except ValueError:
            return []