from typing import Dict, List, Any
import re
import logging

class RecommendationExtractor:
    def process_recommendations(self, raw_recommendations: str) -> List[Dict[str, Any]]:
        """
        Process raw recommendations text into structured data
        """
        try:
            recommendations = []
            # Split into individual product sections
            product_sections = self._split_into_products(raw_recommendations)
            
            for section in product_sections:
                product_data = self._parse_product_section(section)
                if product_data:
                    recommendations.append(product_data)
            
            return recommendations

        except Exception as e:
            logging.error(f"Error processing recommendations: {str(e)}")
            return []

    def _split_into_products(self, text: str) -> List[str]:
        """
        Split raw text into individual product sections
        """
        # Look for numbered sections or product separators
        sections = re.split(r'\d+\.|Product:|===', text)
        return [s.strip() for s in sections if s.strip()]

    def _parse_product_section(self, section: str) -> Dict[str, Any]:
        """
        Parse a product section into structured data
        """
        try:
            # Extract product name and brand
            name_match = re.search(r'(?:Product:)?\s*([^:]+?)(?:\sby\s|\sfrom\s)([^:\n]+)', section)
            if not name_match:
                return None

            name = name_match.group(1).strip()
            brand = name_match.group(2).strip()

            # Extract price
            price_match = re.search(r'Price:\s*(\$\d+(?:\.\d{2})?)', section)
            price = price_match.group(1) if price_match else None

            # Extract ingredients
            ingredients_match = re.search(r'Key Ingredients?:\s*([^\n]+)', section)
            ingredients = []
            if ingredients_match:
                ingredients = [i.strip() for i in ingredients_match.group(1).split(',')]

            # Extract benefits
            benefits_match = re.search(r'Benefits?:\s*([^\n]+)', section)
            benefits = []
            if benefits_match:
                benefits = [b.strip() for b in benefits_match.group(1).split(',')]

            # Extract why it's a good alternative
            alternative_match = re.search(r'Alternative because:\s*([^\n]+)', section)
            alternative_reason = alternative_match.group(1).strip() if alternative_match else None

            return {
                'name': name,
                'brand': brand,
                'price': price,
                'key_ingredients': ingredients,
                'benefits': benefits,
                'alternative_reason': alternative_reason
            }

        except Exception as e:
            logging.error(f"Error parsing product section: {str(e)}")
            return None 