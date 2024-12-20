from bs4 import BeautifulSoup
import requests
from typing import Dict, Any, List
import re
from urllib.parse import urlparse
import logging

class IngredientInfoExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.trusted_domains = [
            'paulaschoice.com',
            'incidecoder.com',
            'skincarisma.com',
            'truthinaging.com',
            'cosmeticsinfo.org',
            'dermreview.com'
        ]

    def extract_ingredients_list(self, product_data: Dict[str, Any]) -> List[str]:
        """Extract and clean ingredients list from product data"""
        ingredients_text = product_data.get('ingredients', '')
        if isinstance(ingredients_text, str):
            # Split by common separators and clean
            ingredients = re.split(r'[,;|]', ingredients_text)
            return [ing.strip() for ing in ingredients if ing.strip()]
        return []

    def analyze_ingredients_data(self, ingredients_list: List[str], search_results: Dict[str, str]) -> Dict[str, Any]:
        """Analyze ingredient information from search results"""
        analyzed_data = {
            'ingredient_details': {},
            'key_actives': [],
            'sources': []
        }

        for ingredient in ingredients_list:
            results = search_results.get(ingredient, '')
            urls = self._extract_urls(results)[:2]  # Get top 2 URLs
            
            ingredient_info = self._analyze_ingredient(ingredient, urls)
            analyzed_data['ingredient_details'][ingredient] = ingredient_info
            
            # Add sources
            analyzed_data['sources'].extend(urls)
            
            # Check if it's a key active ingredient
            if ingredient_info.get('is_active', False):
                analyzed_data['key_actives'].append(ingredient)

        return analyzed_data

    def _analyze_ingredient(self, ingredient: str, urls: List[str]) -> Dict[str, Any]:
        """Analyze a single ingredient from multiple sources"""
        ingredient_info = {
            'benefits': set(),
            'category': None,
            'is_active': False,
            'description': '',
            'safety_info': '',
            'scientific_name': ''
        }

        for url in urls:
            try:
                if not self._is_valid_site(url):
                    continue

                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract information
                benefits = self._extract_benefits(soup, ingredient)
                description = self._extract_description(soup, ingredient)
                safety = self._extract_safety_info(soup, ingredient)
                scientific = self._extract_scientific_info(soup, ingredient)
                category = self._extract_category(soup, ingredient)
                
                # Update ingredient information
                ingredient_info['benefits'].update(benefits)
                if description:
                    ingredient_info['description'] = description
                if safety:
                    ingredient_info['safety_info'] = safety
                if scientific:
                    ingredient_info['scientific_name'] = scientific
                if category:
                    ingredient_info['category'] = category
                
                # Determine if it's an active ingredient
                ingredient_info['is_active'] = self._is_active_ingredient(
                    benefits, description, ingredient
                )

            except Exception as e:
                logging.error(f"Error analyzing ingredient {ingredient} from {url}: {str(e)}")
                continue

        # Convert sets to lists for JSON serialization
        ingredient_info['benefits'] = list(ingredient_info['benefits'])
        return ingredient_info

    def _extract_urls(self, search_results: str) -> List[str]:
        """Extract URLs from search results"""
        urls = []
        for line in search_results.split('\n'):
            if line.startswith('http'):
                urls.append(line.strip())
        return urls

    def _is_valid_site(self, url: str) -> bool:
        """Check if URL is from a trusted skincare/ingredient information site"""
        domain = urlparse(url).netloc.lower()
        return any(trusted in domain for trusted in self.trusted_domains)

    def _extract_benefits(self, soup: BeautifulSoup, ingredient: str) -> set:
        """Extract benefits of the ingredient"""
        benefits = set()
        benefit_patterns = [
            r'benefits?[:\s]+(.*?)(?=\.|$)',
            rf'{ingredient}\s+(?:is|acts as|provides|offers)\s+(.*?)(?=\.|$)',
            r'properties?[:\s]+(.*?)(?=\.|$)'
        ]
        
        text = soup.get_text()
        for pattern in benefit_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                benefit = match.group(1).strip()
                if 5 < len(benefit) < 200:  # Reasonable length for a benefit
                    benefits.add(benefit)
        
        return benefits

    def _extract_description(self, soup: BeautifulSoup, ingredient: str) -> str:
        """Extract general description of the ingredient"""
        description_patterns = [
            rf'{ingredient}\s+is\s+(.*?)(?=\.|$)',
            rf'what is {ingredient}[?:\s]+(.*?)(?=\.|$)',
            rf'{ingredient}:\s+(.*?)(?=\.|$)'
        ]
        
        text = soup.get_text()
        for pattern in description_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                description = match.group(1).strip()
                if 10 < len(description) < 500:  # Reasonable length for description
                    return description
        
        return ""

    def _extract_safety_info(self, soup: BeautifulSoup, ingredient: str) -> str:
        """Extract safety information about the ingredient"""
        safety_patterns = [
            r'safety[:\s]+(.*?)(?=\.|$)',
            r'side effects?[:\s]+(.*?)(?=\.|$)',
            r'precautions?[:\s]+(.*?)(?=\.|$)'
        ]
        
        text = soup.get_text()
        for pattern in safety_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                safety = match.group(1).strip()
                if 10 < len(safety) < 300:  # Reasonable length for safety info
                    return safety
        
        return ""

    def _extract_scientific_info(self, soup: BeautifulSoup, ingredient: str) -> str:
        """Extract scientific name or INCI of the ingredient"""
        scientific_patterns = [
            r'INCI[:\s]+(.*?)(?=\.|$)',
            r'scientific name[:\s]+(.*?)(?=\.|$)',
            r'chemical name[:\s]+(.*?)(?=\.|$)'
        ]
        
        text = soup.get_text()
        for pattern in scientific_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""

    def _extract_category(self, soup: BeautifulSoup, ingredient: str) -> str:
        """Extract ingredient category"""
        category_patterns = [
            r'category[:\s]+(.*?)(?=\.|$)',
            r'type[:\s]+(.*?)(?=\.|$)',
            r'classification[:\s]+(.*?)(?=\.|$)'
        ]
        
        text = soup.get_text()
        for pattern in category_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""

    def _is_active_ingredient(self, benefits: set, description: str, ingredient: str) -> bool:
        """Determine if an ingredient is an active ingredient"""
        active_keywords = {
            'active', 'main ingredient', 'key ingredient', 'primary ingredient',
            'therapeutic', 'treatment', 'potent', 'effective'
        }
        
        # Check benefits and description for active keywords
        text_to_check = ' '.join(benefits).lower() + ' ' + description.lower()
        return any(keyword in text_to_check for keyword in active_keywords) 