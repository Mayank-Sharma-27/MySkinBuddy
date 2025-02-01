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
        You are a knowledgeable skincare product expert focused on providing accurate, evidence-based information.
        
        {user_profile_section}
        
        Your role:
        - Analyze the provided product {product_name} by {brand_name} and its ingredients
        - Focus on answering the specific question asked without adding unnecessary information
        - Base your answers strictly on the provided product context and ingredients
        - Keep responses concise and factual
        
        Response Format:
        1. Start with a brief 1-2 sentence direct answer to the question
        2. If relevant, follow with key points using this format:
           **Key Point Label**: Description with important terms in **bold**
        3. If needed, end with a short conclusion or recommendation
        4. Never use markdown headings (###) or bullet points (-)
        5. Use line breaks between sections for readability
        
        Guidelines:
        - Address the exact question being asked
        - Reference specific ingredients when relevant
        - Avoid marketing language or unsubstantiated claims
        - If information is not in the context, acknowledge the limitation
        - Format important details, ingredients, or recommendations in **bold**
        
        Context for the product:
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
        
        # Get user information
        user_info = context.get("user_information", {})
        user_skin_type = user_info.get("skin_type", "")
        user_skin_issues = ", ".join(user_info.get("skin_issues", []))
        user_additional_info = user_info.get("additional_info", "")
        user_location = user_info.get("location", "")
        
        # Prepare user profile section based on available information
        if any([user_skin_type, user_skin_issues, user_additional_info, user_location]):
            user_profile_section = """
            User Profile Information:
            {}{}{}{}
            """.format(
                f"- Skin Type: {user_skin_type}\n" if user_skin_type else "",
                f"- Skin Issues: {user_skin_issues}\n" if user_skin_issues else "",
                f"- Additional Information: {user_additional_info}\n" if user_additional_info else "",
                f"- Location: {user_location}\n" if user_location else ""
            ).strip()
            
            personalization_guidelines = """
            - Provide personalized advice considering the user's profile information
            - When relevant, explain why the product may or may not be suitable for the user's skin type and issues
            - If the user has specific skin issues, address how the product might help or potentially aggravate them
            """
        else:
            user_profile_section = "Note: No specific user profile information is available."
            personalization_guidelines = ""
        
        # Format prompt
        prompt = self._get_chat_template().format(
            context=context_str,
            question=question,
            chat_history=chat_history,
            product_name=product_name,
            brand_name=brand_name,
            user_profile_section=user_profile_section,
            personalization_guidelines=personalization_guidelines
        )
        
        # Generate response without streaming
        response = self.model.invoke(prompt)
        yield self.format_response(response)