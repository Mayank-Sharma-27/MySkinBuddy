from typing import Dict, AsyncGenerator, List
from .base_agent import BaseAgent

class SimilarProductsAgent(BaseAgent):
    """Agent responsible for finding and comparing similar products"""
    
    SIMILARITY_INTENTS = [
        "What are similar products?",
        "Show me dupes for this",
        "What can I use instead?",
        "Are there alternatives?",
        "Compare this with similar products",
        "What's a good substitute?",
    ]
    
    def can_handle(self, question: str, context: Dict) -> bool:
        question_embedding = self.embeddings.embed_query(question)
        intent_embeddings = self.embeddings.embed_documents(self.SIMILARITY_INTENTS)
        
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
        
        similar_results = pinecone_vector_store.similarity_search(
            question,
            filter={"product_id": product_id, "type": "dupe"},
            k=3
        )
        
        similar_info = "\n".join([doc.page_content for doc in similar_results])
        
        prompt = f"""
        You are a product comparison specialist. Use the following information about similar products to answer the question:
        
        SIMILAR PRODUCTS INFORMATION:
        {similar_info}
        
        QUESTION: {question}
        
        Previous conversation:
        {chat_history}
        
        Provide a detailed comparison of similar products. Include match percentages and specific similarities.
        Highlight key differences and advantages of each product. Be specific about why they are good alternatives.
        """
        
        for chunk in self.model.stream(prompt):
            yield chunk.content 