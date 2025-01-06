from typing import Dict, AsyncGenerator, List
from .base_agent import BaseAgent

class EnvironmentalAgent(BaseAgent):
    """
    Agent responsible for handling environment and climate related questions
    """
    
    def can_handle(self, question: str, context: Dict) -> bool:
        # TODO: Implement logic to determine if question needs environmental context
        return False
        
    def get_required_context(self) -> List[str]:
        return ["location", "climate"]
        
    async def process(
        self,
        question: str,
        context: Dict,
        chat_history: List[Dict]
    ) -> AsyncGenerator[str, None]:
        # TODO: Implement environmental specific processing
        yield "Not implemented yet" 