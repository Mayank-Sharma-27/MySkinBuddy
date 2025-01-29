from typing import Dict, Generator, List
from .base_agent import BaseAgent
from ..embeddings import pinecone_vector_store
import re

class PricingAgent(BaseAgent):
    """Agent responsible for handling pricing related queries"""
    
    PRICING_PATTERNS = [
        r"cost",
        r"price",
        r"how much",
        r"cheaper",
        r"worth",
        r"deal",
        r"buy",
        r"expensive",
        r"affordable"
    ]
    
    def can_handle(self, question: str, context: Dict) -> bool:
        print(f"Pricing Agent checking: {question}")
        question_lower = question.lower()
        
        # Check if any pricing pattern matches
        for pattern in self.PRICING_PATTERNS:
            if re.search(pattern, question_lower):
                print(f"Pricing Agent matched pattern: {pattern}")
                return True
                
        return False
    
    def get_required_context(self) -> List[str]:
        return ["product_id"]
    
    def process(
        self,
        question: str,
        context: Dict,
        chat_history: List[Dict]
    ) -> Generator[str, None, None]:
        product_id = context.get("product_id")
        product_name = context.get("preloaded_context", {}).get("product", {}).get("metadata", {}).get("product", "")
        brand_name = context.get("preloaded_context", {}).get("product", {}).get("metadata", {}).get("brand", "")
        
        pricing_results = self.vector_store.similarity_search(
            question,
            filter={"product_id": product_id, "type": "pricing"},
            k=1
        )
        
        pricing_info = "\n".join([doc.page_content for doc in pricing_results])
        
        prompt = f"""
        You are a pricing assistant for {product_name} by {brand_name}. Provide a clear and direct answer about the product's price.

        Here is the pricing information:
        {pricing_info}

        Rules:
        1. Start with the price directly - "This product costs $X"
        2. If there are multiple retailers, list them clearly
        3. Keep the response short and focused on pricing
        4. Don't mention anything about real-time pricing or checking websites
        5. Only use the pricing information provided above

        Question: {question}
        """
        
        response = self.model.invoke(prompt)
        yield self.format_response(response) 