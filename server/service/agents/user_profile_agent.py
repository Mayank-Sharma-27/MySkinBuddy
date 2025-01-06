from typing import Dict, AsyncGenerator, List
from .base_agent import BaseAgent

class UserProfileAgent(BaseAgent):
    """
    Agent responsible for handling user-specific questions and maintaining user context
    """
    
    def can_handle(self, question: str, context: Dict) -> bool:
        # TODO: Implement logic to determine if question needs user profile context
        return False
        
    def get_required_context(self) -> List[str]:
        return ["user_profile"]
        
    async def process(
        self,
        question: str,
        context: Dict,
        chat_history: List[Dict]
    ) -> AsyncGenerator[str, None]:
        # TODO: Implement user profile specific processing
        yield "Not implemented yet" 