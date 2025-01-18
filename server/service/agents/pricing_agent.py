from typing import Dict, AsyncGenerator, List
from .base_agent import BaseAgent

class PricingAgent(BaseAgent):
    """Agent responsible for handling pricing related queries"""
    
    PRICING_INTENTS = [
        "How much does this cost?",
        "Where can I buy this cheapest?",
        "Is there a cheaper alternative?",
        "Compare prices across retailers",
        "What's the best deal for this product?",
        "Is this product worth the price?",
    ]
    
    def can_handle(self, question: str, context: Dict) -> bool:
        question_embedding = self.embeddings.embed_query(question)
        intent_embeddings = self.embeddings.embed_documents(self.PRICING_INTENTS)
        
        max_similarity = 0
        for intent_embedding in intent_embeddings:
            similarity = sum(q * i for q, i in zip(question_embedding, intent_embedding))
            max_similarity = max(max_similarity, similarity)
            
        return max_similarity > 0.75
    
    def get_required_context(self) -> List[str]:
        return ["product_id"]
    
    async def process(
        self,
        question: str,
        context: Dict,
        chat_history: List[Dict]
    ) -> AsyncGenerator[str, None]:
        product_id = context.get("product_id")
        
        pricing_results = pinecone_vector_store.similarity_search(
            question,
            filter={"product_id": product_id, "type": "pricing"},
            k=1
        )
        
        pricing_info = "\n".join([doc.page_content for doc in pricing_results])
        
        prompt = f"""
        You are a pricing specialist. Use the following pricing information to answer the question:
        
        PRICING INFORMATION:
        {pricing_info}
        
        QUESTION: {question}
        
        Previous conversation:
        {chat_history}
        
        Provide a clear response focusing on pricing details. Include specific prices and retailers when available.
        Compare prices if multiple retailers are mentioned.
        """
        
        for chunk in self.model.stream(prompt):
            yield chunk.content 