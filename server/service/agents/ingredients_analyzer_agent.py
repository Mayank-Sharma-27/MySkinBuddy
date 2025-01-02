from typing import Dict, Any, List
import logging
from langchain_community.utilities import GoogleSearchAPIWrapper
from service.extractors.ingredient_info_extractor import IngredientInfoExtractor

class IngredientAnalyzerAgent:
    def __init__(self):
        self.search_tool = GoogleSearchAPIWrapper()
        self.extractor = IngredientInfoExtractor()
        
    def analyze_ingredients(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze ingredients and their benefits
        """
        try:
            # Extract ingredients list from product data
            ingredients_list = self.extractor.extract_ingredients_list(product_data)
            
            # For each ingredient, search and analyze information
            search_results = {}
            for ingredient in ingredients_list:
                search_query = f"{ingredient} skincare ingredient benefits research"
                results = self.search_tool.run(search_query)
                search_results[ingredient] = results

            analyzed_data = self.extractor.analyze_ingredients_data(ingredients_list, search_results)
            
            return {
                'ingredients_list': ingredients_list,
                'analysis': analyzed_data,
                'sources': analyzed_data.get('sources', [])
            }
            
        except Exception as e:
            logging.error(f"Error in analyze_ingredients: {str(e)}")
            raise    