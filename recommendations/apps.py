from django.apps import AppConfig

class RecommendationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommendations'
    
    def ready(self):
        # Import signals or other startup code
        from . import signals  # We'll create this next