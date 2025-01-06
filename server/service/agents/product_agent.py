from typing import Dict, AsyncGenerator, List
from .base_agent import BaseAgent
from langchain.prompts import ChatPromptTemplate

class ProductAgent(BaseAgent):
    """
    Agent responsible for handling product-specific questions using product context
    This is our primary agent that handles basic product information
    """
    
    def can_handle(self, question: str, context: Dict) -> bool:
        # This is our default agent, so it can handle any question
        return True
        
    def get_required_context(self) -> List[str]:
        return ["product"]
        
    def _get_chat_template(self) -> ChatPromptTemplate:
        system = """
        You are an expert on human skincare products. You have detailed knowledge of chemicals used in skin care products that you can advise 
        people on what product to use and when.
        When helping the user with the question you have to assume that the role of user's personal skin care assistant you knows everything about the product {product_name} with brand {brand_name}. 
        You should have all the information about the product.
        specially ingredients, benefits, and other information.
        You have to answer the user's question based on user's question and the related contexts.
        Please make sure to give concise and clear answers do not give long answers so that the user can understand the answer.
        If here are any key information that you want to mention return it int ** format. Also if you name any ingredient return it in ** format.

        Here are the contexts which will help you answer question and know more about yourself:
        {context}

        Please use the information already provided in the Previous conversation to help the user with the question.
        {chat_history}

        Current question: {question}
        """

        human = """
        User Question: {question}
        """
        
        return ChatPromptTemplate.from_messages([
            ("system", system),
            ("human", human)
        ])
        
    async def process(
        self,
        question: str,
        context: Dict,
        chat_history: List[Dict]
    ) -> AsyncGenerator[str, None]:
        # Get product context
        product_doc = context.get("preloaded_context", {}).get("product", {})
        product_info = product_doc.get("page_content", "")
        
        # Extract ingredients from product info
        ingredients_start = product_info.find("Ingredients :") + len("Ingredients :")
        product_details = product_info[:ingredients_start].strip()
        ingredients_list = product_info[ingredients_start:].strip()
        
        # Build context string
        context_str = (
            f"PRODUCT INFO:\n{product_details}\n\n"
            f"INGREDIENTS:\n{ingredients_list}\n\n"
        )
        
        # Get product metadata
        product_name = product_doc.get("metadata", {}).get("product", "")
        brand_name = product_doc.get("metadata", {}).get("brand", "")
        
        # Format prompt
        prompt = self._get_chat_template().format(
            context=context_str,
            question=question,
            chat_history=[],  # TODO: Format chat history
            product_name=product_name,
            brand_name=brand_name
        )
        
        # Generate response
        for chunk in self.model.stream(prompt):
            yield chunk.content 