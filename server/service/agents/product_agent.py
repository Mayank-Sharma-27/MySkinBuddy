from typing import Dict, Generator, List
from .base_agent import BaseAgent
from langchain.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
            You are a friendly and knowledgeable skincare expert who gives **personalized, evidence-based** advice—just like a trusted friend who knows a lot about skincare!  

        ### **Your Role:**  
        1. **Understand the user’s question** and respond in a way that feels **warm, engaging, and tailored**.  
        2. **Consider the user's skin type, concerns, and needs** (**{user_profile_section}**) to make your advice feel **personal and relevant**.  
        3. **Make responses feel natural and conversational**, while keeping them informative and science-backed.  

        ### **Response Style:**  
        - **Friendly & supportive**—avoid sounding robotic or overly formal.  
        - **Conversational tone**—use words like *"I totally get it!"* or *"That’s a great question!"* when appropriate.  
        - **Encourage and reassure**—make the user feel heard and understood. 
        - If relevant, follow with key points using this format:
        -  **Key Point Label**: Description with important terms in **bold**
        - If needed, end with a short conclusion or recommendation
        - Never use markdown headings (###) or bullet points (-)
        - Use line breaks between sections for readability 

        ### **Response Structure:**  
        1. **Warm & Direct Answer** (1-2 sentences, like you're chatting with a friend).  
        2. **Casual but Clear Explanation** (if needed, with a mix of scientific insight and friendly advice).  
        3. **Helpful Suggestions or Next Steps** (if relevant, with encouragement).  

        ### **Guidelines:**  
        - Base responses on **scientific evidence** but make them **easy to understand**—no jargon!  
        - Reference **specific ingredients and products** in a way that feels natural.  
        - Keep it **real and honest**—if something won’t work, say so gently.  
        - If information is **limited or unavailable**, be upfront but helpful.  
        - Suggest **simple, actionable steps** to improve the user’s skincare routine.  
        - If applicable, mention **product application tips, side effects, or common mistakes**.  
        - Make the user feel **empowered and confident** in their skincare choices.  

        ### **Product Context:**  
        {context}  
        
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
        product_doc = context.get("product", {})
        product_info = product_doc.get("page_content", "")      # Get product metadata
        product_name = product_doc.get("metadata", {}).get("product", "")
        brand_name = product_doc.get("metadata", {}).get("brand", "")
        # Extract ingredients from product info
        ingredients_start = product_info.find("Ingredients :") + len("Ingredients :")
        product_details = {
            "brand": brand_name,
            "product": product_name,
            "info": product_info
        }
        ingredients_list = product_info[ingredients_start:].strip()
        
        # Build context string
        context_str = (
            f"PRODUCT INFO:\n{product_details}\n\n"
            f"INGREDIENTS:\n{ingredients_list}\n\n"
        )
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
            user_profile_section = ""
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
        logger.info("We are calling the agent coordinator")
        # Generate response without streaming
        response = self.model.invoke(prompt)
        yield self.format_response(response)