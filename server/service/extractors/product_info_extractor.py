from bs4 import BeautifulSoup
import requests
from typing import Dict, Any, List
import re
import logging

class ProductInfoExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def analyze_top_results(self, search_results: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze search results and return consolidated product information
        """
        all_info = []
        
        for result in search_results[:3]:  # Analyze top 3 results
            try:
                logging.info(f"Analyzing URL: {result['link']}")
                
                # Get basic info from snippet
                info = {
                    'description': result['snippet'],
                    'source': result['link']
                }
                
                # Try to get more detailed info from webpage
                try:
                    response = requests.get(result['link'], headers=self.headers, timeout=10)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    webpage_info = self._extract_product_info(soup)
                    
                    # Update info with webpage data if found
                    if webpage_info['description']:
                        info['description'] = webpage_info['description']
                    info.update({k: v for k, v in webpage_info.items() if v})
                    
                except Exception as e:
                    logging.warning(f"Could not fetch webpage {result['link']}: {str(e)}")
                
                all_info.append(info)
                
            except Exception as e:
                logging.error(f"Error analyzing URL {result['link']}: {str(e)}")
                continue

        # Consolidate information from all sources
        return self._consolidate_information(all_info)

    def _extract_product_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract all product information from webpage"""
        return {
            'description': self._extract_description(soup),
            'how_to_use': self._extract_how_to_use(soup),
            'benefits': self._extract_benefits(soup),
            'key_features': self._extract_features(soup)
        }

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract product description"""
        description = ""
        
        # Common description selectors
        selectors = [
            ['div', {'class_': re.compile(r'product.*description|description|about|overview', re.I)}],
            ['div', {'id': re.compile(r'product.*description|description|about|overview', re.I)}],
            ['section', {'class_': re.compile(r'description|about|overview', re.I)}],
            ['meta', {'name': 'description'}]
        ]
        
        for tag, attrs in selectors:
            elements = soup.find_all(tag, attrs)
            for elem in elements:
                if tag == 'meta':
                    text = elem.get('content', '')
                else:
                    text = elem.get_text(strip=True)
                if text and len(text) > len(description):
                    description = text

        return description

    def _extract_ingredients(self, soup: BeautifulSoup) -> List[str]:
        """Extract ingredients list"""
        ingredients = []
        
        # Look for ingredients sections
        for elem in soup.find_all(['div', 'section', 'p'], text=re.compile(r'ingredients?|key ingredients', re.I)):
            next_elem = elem.find_next(['ul', 'p', 'div'])
            if next_elem:
                if next_elem.name == 'ul':
                    items = [li.text.strip() for li in next_elem.find_all('li')]
                else:
                    # Split text by common separators
                    text = next_elem.get_text(strip=True)
                    items = [i.strip() for i in re.split(r',|\u2022|\n', text)]
                
                ingredients.extend([i for i in items if i and not i.lower().startswith('ingredient')])

        return list(set(ingredients))

    def _extract_how_to_use(self, soup: BeautifulSoup) -> str:
        """Extract usage instructions"""
        keywords = ['how to use', 'directions', 'application', 'usage', 'how to apply']
        
        # Case-insensitive regex pattern for all keywords
        pattern = '|'.join(keywords)
        
        # Find sections with case-insensitive matching
        for section in soup.find_all(['div', 'section', 'p'], text=re.compile(pattern, re.I)):
            next_elem = section.find_next(['div', 'p', 'ul'])
            if next_elem:
                text = next_elem.get_text(strip=True)
                if text and len(text) > 20:  # Ensure it's meaningful content
                    return text
                
        # Try finding elements with class/id containing these keywords
        for tag in ['div', 'section']:
            for keyword in keywords:
                elements = soup.find_all(tag, class_=re.compile(keyword, re.I))
                elements.extend(soup.find_all(tag, id=re.compile(keyword, re.I)))
                
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 20:
                        return text
        
        return ""

    def _extract_benefits(self, soup: BeautifulSoup) -> List[str]:
        """Extract product benefits"""
        benefits = []
        
        for keyword in ['benefits', 'what it does', 'why you\'ll love it']:
            sections = soup.find_all(['div', 'section', 'p'], text=re.compile(keyword, re.I))
            for section in sections:
                next_elem = section.find_next(['ul', 'p'])
                if next_elem:
                    if next_elem.name == 'ul':
                        items = [li.text.strip() for li in next_elem.find_all('li')]
                    else:
                        text = next_elem.get_text(strip=True)
                        items = [b.strip() for b in text.split('.')]
                    benefits.extend([b for b in items if b and len(b) > 10])

        return list(set(benefits))

    def _extract_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract key features"""
        features = []
        
        for keyword in ['features', 'highlights', 'key benefits']:
            sections = soup.find_all(['div', 'section', 'p'], text=re.compile(keyword, re.I))
            for section in sections:
                next_elem = section.find_next(['ul', 'p'])
                if next_elem:
                    if next_elem.name == 'ul':
                        items = [li.text.strip() for li in next_elem.find_all('li')]
                    else:
                        text = next_elem.get_text(strip=True)
                        items = [f.strip() for f in text.split('.')]
                    features.extend([f for f in items if f and len(f) > 10])

        return list(set(features))

    def _consolidate_information(self, all_info: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Consolidate information from multiple sources"""
        
        # Get the longest description
        descriptions = [info['description'] for info in all_info if info.get('description')]
        best_description = max(descriptions, key=len) if descriptions else ""

        # Combine all unique items
        consolidated = {
            'description': best_description,
            'ingredients': [],
            'how_to_use': "",
            'benefits': [],
            'key_features': [],
            'sources': [info['source'] for info in all_info]
        }

        # Get the longest how_to_use
        how_to_use_texts = [info['how_to_use'] for info in all_info if info.get('how_to_use')]
        if how_to_use_texts:
            consolidated['how_to_use'] = max(how_to_use_texts, key=len)

        # Combine unique items from all sources
        for info in all_info:
            if info.get('ingredients'):
                consolidated['ingredients'].extend(info['ingredients'])
            if info.get('benefits'):
                consolidated['benefits'].extend(info['benefits'])
            if info.get('key_features'):
                consolidated['key_features'].extend(info['key_features'])

        # Remove duplicates and keep lists unique
        consolidated['ingredients'] = list(set(consolidated['ingredients']))
        consolidated['benefits'] = list(set(consolidated['benefits']))
        consolidated['key_features'] = list(set(consolidated['key_features']))

        return consolidated

    def aggregate_information(self, analyzed_results: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate information from analyzed search results
        """
        print(f"Type of analyzed_results: {type(analyzed_results)}")
        print(f"Content of analyzed_results: {analyzed_results}")
        
        aggregated = {
            'description': '',
            'how_to_use': '',
            'benefits': [],
            'key_features': []
        }
        
        if isinstance(analyzed_results, str):
            aggregated['description'] = analyzed_results
            return aggregated
        
        if isinstance(analyzed_results, dict):
            analyzed_results = [analyzed_results]
        
        for result in analyzed_results:
            if isinstance(result, str):
                if len(result) > len(aggregated['description']):
                    aggregated['description'] = result
                continue
            
            # Get longest description
            if 'description' in result and len(result['description']) > len(aggregated['description']):
                aggregated['description'] = result['description']
            
            # Get longest how_to_use
            if 'how_to_use' in result and len(result['how_to_use']) > len(aggregated['how_to_use']):
                aggregated['how_to_use'] = result['how_to_use']
            
            # Combine list fields
            for key in ['benefits', 'key_features']:
                if key in result and result[key]:
                    aggregated[key].extend(result[key])
        
        # Remove duplicates while preserving order
        for key in ['benefits', 'key_features']:
            aggregated[key] = list(dict.fromkeys(aggregated[key]))
        
        return aggregated