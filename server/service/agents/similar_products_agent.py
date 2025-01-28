from typing import Dict, Generator, List
from .base_agent import BaseAgent
from ..embeddings import pinecone_vector_store
import re

class SimilarProductsAgent(BaseAgent):
    """Agent responsible for finding and comparing similar products"""
    
    SIMILARITY_PATTERNS = [
        r"similar",
        r"dupe",
        r"alternative",
        r"like this",
        r"substitute",
        r"instead",
        r"compare",
        r"other products",
        r"comparable"
    ]
    
    def can_handle(self, question: str, context: Dict) -> bool:
        print(f"Similar Products Agent checking: {question}")
        question_lower = question.lower()
        
        # Check if any similarity pattern matches
        for pattern in self.SIMILARITY_PATTERNS:
            if re.search(pattern, question_lower):
                print(f"Similar Products Agent matched pattern: {pattern}")
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
        
        similar_results = self.vector_store.similarity_search(
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