from typing import Dict, AsyncGenerator, List
from .base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    """
    Agent responsible for advanced research using all available embeddings
    """
    
    def can_handle(self, question: str, context: Dict) -> bool:
        # Keywords that indicate need for detailed research
        research_keywords = [
            "compare", "difference", "similar", "dupe",
            "ingredient", "composition", "price",
            "cheaper", "expensive", "alternative",
            "benefits", "effects", "research",
            "study", "clinical", "evidence"
        ]
        return any(keyword in question.lower() for keyword in research_keywords)
    
    def get_required_context(self) -> List[str]:
        return ["product_id"]
    
    async def process(
        self,
        question: str,
        context: Dict,
        chat_history: List[Dict]
    ) -> AsyncGenerator[str, None]:
        product_id = context.get("product_id")
        question_lower = question.lower()
        
        # Determine what type of research is needed
        research_context = []
        
        # Get ingredient information if needed
        if any(word in question_lower for word in ["ingredient", "contain", "composition"]):
            ingredient_results = pinecone_vector_store.similarity_search(
                question,
                filter={"product_id": product_id, "type": "ingredients"},
                k=2
            )
            research_context.extend(ingredient_results)
        
        # Get similar products if needed
        if any(word in question_lower for word in ["compare", "similar", "dupe", "alternative"]):
            dupe_results = pinecone_vector_store.similarity_search(
                question,
                filter={"product_id": product_id, "type": "dupe"},
                k=2
            )
            research_context.extend(dupe_results)
        
        # Get pricing information if needed
        if any(word in question_lower for word in ["price", "cost", "cheaper", "expensive"]):
            price_results = pinecone_vector_store.similarity_search(
                question,
                filter={"product_id": product_id, "type": "pricing"},
                k=1
            )
            research_context.extend(price_results)
        
        # Combine all research context
        research_info = "\n".join([doc.page_content for doc in research_context])
        
        prompt = f"""
        You are a skincare research expert. Use the following detailed information to answer the question:
        
        RESEARCH INFORMATION:
        {research_info}
        
        QUESTION: {question}
        
        Previous conversation:
        {chat_history}
        
        Please provide a detailed, evidence-based response. Highlight key findings in **bold** and any specific ingredients in **bold** as well.
        Focus on being accurate and specific while maintaining a helpful and clear tone.
        """
        
        for chunk in self.model.stream(prompt):
            yield chunk.content 