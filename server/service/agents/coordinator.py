from typing import Dict, AsyncGenerator, List
from .base_agent import BaseAgent
from .product_agent import ProductAgent

class AgentCoordinator:
    """
    Coordinates multiple agents to handle user questions.
    Determines which agents should handle each question and combines their responses.
    """
    
    def __init__(self):
        """
        Initialize coordinator with ProductAgent as the default
        """
        self.default_agent = ProductAgent()
        self.agents = []  # Additional agents can be added later
        
    async def process_question(
        self,
        question: str,
        context: Dict,
        chat_history: List[Dict]
    ) -> AsyncGenerator[str, None]:
        """
        Process a question using appropriate agents
        
        Args:
            question: The user's question
            context: Current conversation context
            chat_history: Conversation history
            
        Returns:
            Generator[str, None, None]: Stream of response chunks
        """
        # For now, just use the default product agent
        async for chunk in self.default_agent.process(question, context, chat_history):
            yield chunk
            
        # Extract and store any new insights
        # TODO: Implement insight gathering from all agents 