from typing import Dict, List, Any
import logging
from service.models.perplexity import get_perplexity_response
from service.extractors.recommendation_extractor import RecommendationExtractor

class ProductRecommendationsAgent:
    def __init__(self):
        self.extractor = RecommendationExtractor()

    def recommend_products(self, product_id: str, user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get personalized product recommendations using Perplexity
        """
        try:
            # Build recommendation prompt
            prompt = self._build_recommendation_prompt(product_id, user_preferences)
            
            # Get recommendations from Perplexity
            raw_recommendations = get_perplexity_response(prompt)
            
            # Process and structure the recommendations
            recommendations = self.extractor.process_recommendations(raw_recommendations)
            
            return recommendations

        except Exception as e:
            logging.error(f"Error in recommend_products: {str(e)}")
            raise

    def _build_recommendation_prompt(self, product_id: str, user_preferences: Dict[str, Any]) -> str:
        """
        Build a detailed prompt for product recommendations
        """
        skin_type = user_preferences.get('skin_type', 'all')
        concerns = user_preferences.get('concerns', [])
        price_range = user_preferences.get('price_range', 'any')
        
        prompt = f"""
        As a skincare expert, recommend 5 products similar to product ID {product_id}, considering:

        Criteria:
        - Similar active ingredients and formulation
        - Suitable for {skin_type} skin type
        - Addresses concerns: {', '.join(concerns) if concerns else 'any'}
        - Price range: {price_range}
        
        For each product, provide:
        1. Product name and brand
        2. Key active ingredients
        3. Main benefits
        4. Price
        5. Why it's a good alternative

        Format each product recommendation as:
        Product: [Name] by [Brand]
        Price: [Price]
        Key Ingredients: [List of ingredients]
        Benefits: [List of benefits]
        Alternative because: [Reason]
        """
        
        return prompt.strip()