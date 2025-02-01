from typing import Dict, Generator, List
from .base_agent import BaseAgent
from .product_agent import ProductAgent
from .pricing_agent import PricingAgent
from .ingredient_agent import IngredientAgent
from .similar_products_agent import SimilarProductsAgent

class AgentCoordinator:
    """
    Coordinates multiple specialized agents to handle user questions.
    """
    
    def __init__(self):
        self.product_agent = ProductAgent()
        self.pricing_agent = PricingAgent()
        self.ingredient_agent = IngredientAgent()
        self.similar_products_agent = SimilarProductsAgent()
        
    def process_question(
        self,
        question: str,
        context: Dict,
        chat_history: List[Dict]
    ) -> Generator[str, None, None]:
        """
        Process a question using appropriate agents
        """
        agents_to_use = []
        print("Processing question in coordinator")
        
        agents_to_use.append(self.product_agent)
        
        # For now, just use the first capable agent
        agent = agents_to_use[0]
        
        for chunk in agent.process(question, context, chat_history):
            yield chunk 