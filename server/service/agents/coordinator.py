from typing import Dict, AsyncGenerator, List
from .base_agent import BaseAgent
from .product_agent import ProductAgent
from .research_agent import ResearchAgent

class AgentCoordinator:
    """
    Coordinates multiple agents to handle user questions.
    """
    
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.product_agent = ProductAgent()
        
    async def process_question(
        self,
        question: str,
        context: Dict,
        chat_history: List[Dict]
    ) -> AsyncGenerator[str, None]:
        """
        Process a question using appropriate agents
        """
        # First check if research agent should handle it
        if self.research_agent.can_handle(question, context):
            async for chunk in self.research_agent.process(question, context, chat_history):
                yield chunk
        else:
            # Default to product agent for basic questions
            async for chunk in self.product_agent.process(question, context, chat_history):
                yield chunk 