from typing import Dict, AsyncGenerator, List
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
        
    async def process_question(
        self,
        question: str,
        context: Dict,
        chat_history: List[Dict]
    ) -> AsyncGenerator[str, None]:
        """
        Process a question using appropriate agents, potentially combining multiple responses
        """
        agents_to_use = []
        
        # Determine which agents should handle the question
        if self.pricing_agent.can_handle(question, context):
            agents_to_use.append(self.pricing_agent)
        if self.ingredient_agent.can_handle(question, context):
            agents_to_use.append(self.ingredient_agent)
        if self.similar_products_agent.can_handle(question, context):
            agents_to_use.append(self.similar_products_agent)
        if not agents_to_use or self.product_agent.can_handle(question, context):
            agents_to_use.append(self.product_agent)
        
        # If multiple agents are needed, gather all responses
        responses = []
        for agent in agents_to_use:
            agent_response = ""
            async for chunk in agent.process(question, context, chat_history):
                agent_response += chunk
            responses.append(agent_response)
        
        # Combine responses if multiple agents were used
        if len(responses) > 1:
            combined_info = "\n\n".join(responses)
            summary_prompt = f"""
            Combine and summarize the following information into a coherent response:
            
            {combined_info}
            
            Create a well-organized response that flows naturally and doesn't repeat information.
            """
            
            async for chunk in self.product_agent.model.stream(summary_prompt):
                yield chunk.content
        else:
            # If only one agent was used, return its response directly
            yield responses[0] 