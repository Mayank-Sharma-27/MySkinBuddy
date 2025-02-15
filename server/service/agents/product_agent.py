from typing import Dict, Generator, List, Optional
from .base_agent import BaseAgent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import logging
import re
from ..utils.response_formatter import ResponseFormatter

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
        You are a friendly skincare assistant with expert-level knowledge of skincare products and ingredients. 
        If the question asked by the user is not related to skincare or skin care product do not event respond and stop the conversation. Do not entertain any question other than skin care products or related questions
        Your role is to provide **personalized, accurate, and evidence-based** responses. If possible return the emoji of the product or ingredient that is relevant to the question.

        Format your responses using proper markdown headings:
        - Use ## for main titles (e.g. "## Ingredient Analysis")
        - Use ### for section headings (e.g. "### Main Ingredients")
        - Never use single # for headings
        - Use **text** only for emphasis within paragraphs
        - Use bullet points (•) for lists
        
        **Guidelines:**  
        - Use the provided information in the product context, user profile, chat history, your own knowledge base and real time search to answer the question to the best of your ability.  
        - If a question is outside skincare, reply: "I specialize in skincare product recommendations."  
        - Keep answers **concise** yet informative.  
        - If you cannot find any information to help the user, say: **"I don't have that information in the current context."** 
        - Do not print very long think sections, just summarize the thought process and provide the final answer.  

        **User Profile:**  
        {user_profile_section}  

        **Product Context:**  
        {context}  

        **User's Question:**  
        {question}  
        """

        return ChatPromptTemplate.from_messages([
            ("system", system),
            MessagesPlaceholder(variable_name=self.memory.memory_key),
            ("human", "{question}")
        ])
        
    def process(
        self,
        question: str,
        context: Dict,
        chat_history: Optional[List[Dict]] = None
    ) -> Generator[Dict, None, None]:
        product_doc = context.get("product", {})
        product_id = product_doc.get("metadata", {}).get("product_id", "default")
        # Create product-specific memory key
        self.set_memory_key(f"chat_history_{product_id}")
        
        context["product_info"] = self._format_product_info(product_doc)
        context["user_profile_section"] = self._format_user_profile(context.get("user_information", {}))
        
        # Use the chain
        chain = self.setup_chain()
        chain_input = self._combine_input(question, context)
        
        # Track full response and citations
        full_response = ""
        citations = []
        # Stream the content first
        for chunk in chain.stream(chain_input):
            content = chunk.content
            full_response += content
            
            # Collect citations from chunk
            chunk_citations = chunk.additional_kwargs.get('citations', [])
            if chunk_citations:
                citations.extend(chunk_citations)
                
            if content.strip():
                yield ResponseFormatter.format_chunk(content)
        
        # After content is done, send citations
        if citations:
            yield ResponseFormatter.format_citation('\n\n---\n\nTo learn more, you can refer to these sources:\n')
            
            for i, url in enumerate(citations, 1):
                domain = re.search(r'https?://(?:www\.)?([^/]+)', url)
                if domain:
                    site_name = domain.group(1).replace('.com', '').replace('.org', '')
                    site_name = ' '.join(word.capitalize() for word in site_name.split('.'))
                    yield ResponseFormatter.format_citation(
                        f'\n{i}. {site_name} - [Read more]({url})'
                    )
                else:
                    yield ResponseFormatter.format_citation(
                        f'\n{i}. [Source {i}]({url})'
                    )
        
        # Save to memory
        try:
            cleaned_response = re.sub(r'<think>[\s\S]*?</think>', '', full_response, flags=re.DOTALL).strip()
            self.memory.save_context(
                {"input": question}, 
                {"output": cleaned_response}
            )
            logger.info("Saving to memory done")
        except Exception as e:
            logger.error(f"Error saving to memory: {str(e)}")
        
    def _format_product_info(self, product_doc: Dict) -> str:
        """Format product information for the prompt"""
        product_info = product_doc.get("page_content", "")
        product_name = product_doc.get("metadata", {}).get("product", "")
        brand_name = product_doc.get("metadata", {}).get("brand", "")
        
        return f"""
        Brand: {brand_name}
        Product: {product_name}
        Details: {product_info}
        """
        
    def _format_user_profile(self, user_info: Dict) -> str:
        """Format user profile information if available"""
        if not user_info:
            return ""
            
        profile_parts = []
        if skin_type := user_info.get("skin_type"):
            profile_parts.append(f"Skin Type: {skin_type}")
        if skin_issues := user_info.get("skin_issues"):
            profile_parts.append(f"Skin Issues: {', '.join(skin_issues)}")
        if location := user_info.get("location"):
            profile_parts.append(f"Location: {location}")
        if additional_info := user_info.get("additional_info"):
            profile_parts.append(f"Additional Information: {additional_info}")
            
        if profile_parts:
            return "USER PROFILE:\n" + "\n".join(profile_parts)
        return ""