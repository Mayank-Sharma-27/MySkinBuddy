from typing import Dict, Generator, List
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
        You are an expert on human skincare products. 
        When helping the user with the question you have to assume that the role of a personal skin care assistant and knows everything about the product {product_name} with brand {brand_name}. 
        While answering the question to the user try to understand the user's question and answer the question based on user's question and the related contexts and do not repeat the product name again and again.
        
        Please always try to be to the point and do not confuse the user with long answers.
        While answering the question also please try to keep in mind the ingredients of the product which are in the context.
        Please return the part which you think should be highlighted using **bold** in the answer.
        Here are the contexts which will help you answer question and know more about the product:
        {context}

        Current question: {question}
        """

        human = """
        User Question: {question}
        """
        
        return ChatPromptTemplate.from_messages([
            ("system", system),
            ("human", human)
        ])
        
    def process(
        self,
        question: str,
        context: Dict,
        chat_history: List[Dict]
    ) -> Generator[str, None, None]:
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
            chat_history=chat_history,
            product_name=product_name,
            brand_name=brand_name
        )
        
        # Generate response without streaming
        response = self.model.invoke(prompt)
        #print(self.format_response(response))
        yield self.format_response(response) 