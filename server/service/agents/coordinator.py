from typing import Dict, Generator, List
from .base_agent import BaseAgent
from .product_agent import ProductAgent

class AgentCoordinator:
    """
    Coordinates multiple specialized agents to handle user questions.
    """
    
    def __init__(self):
        self.product_agent = ProductAgent()
        
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
        
        agents_to_use.append(self.product_agent)
        
        # For now, just use the first capable agent
        agent = agents_to_use[0]
        
        for chunk in agent.process(question, context, chat_history):
            yield chunk 