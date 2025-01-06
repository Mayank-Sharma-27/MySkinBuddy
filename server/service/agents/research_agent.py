from typing import Dict, AsyncGenerator, List
from .base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    """
    Agent responsible for real-time research and information gathering
    """
    
    def can_handle(self, question: str, context: Dict) -> bool:
        # TODO: Implement logic to determine if question needs external research
        return False
        
    def get_required_context(self) -> List[str]:
        return ["search_scope"]
        
    async def process(
        self,
        question: str,
        context: Dict,
        chat_history: List[Dict]
    ) -> AsyncGenerator[str, None]:
        # TODO: Implement research specific processing
        yield "Not implemented yet" 