from typing import Dict, AsyncGenerator, List
from .base_agent import BaseAgent

class IngredientAgent(BaseAgent):
    """Agent responsible for ingredient analysis and information"""
    
    INGREDIENT_INTENTS = [
        "What are the key ingredients?",
        "Tell me about this ingredient",
        "Is this ingredient safe?",
        "What does this ingredient do?",
        "Are there any harmful ingredients?",
        "What are the active ingredients?",
        "How does this ingredient work?",
    ]
    
    def can_handle(self, question: str, context: Dict) -> bool:
        question_embedding = self.embeddings.embed_query(question)
        intent_embeddings = self.embeddings.embed_documents(self.INGREDIENT_INTENTS)
        
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
        
        ingredient_results = pinecone_vector_store.similarity_search(
            question,
            filter={"product_id": product_id, "type": "ingredients"},
            k=2
        )
        
        ingredient_info = "\n".join([doc.page_content for doc in ingredient_results])
        
        prompt = f"""
        You are a cosmetic ingredient expert. Use the following ingredient information to answer the question:
        
        INGREDIENT INFORMATION:
        {ingredient_info}
        
        QUESTION: {question}
        
        Previous conversation:
        {chat_history}
        
        Provide a detailed response about the ingredients. Highlight key ingredients in **bold**.
        Include both benefits and any potential concerns. Be specific about what each ingredient does.
        """
        
        for chunk in self.model.stream(prompt):
            yield chunk.content 