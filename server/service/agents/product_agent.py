from typing import Dict, Generator, List, Optional
from .base_agent import BaseAgent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import logging
import re
import json
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
            You are a specialized skincare product assistant. You MUST ONLY answer questions about skincare products based on the information provided in the context. You cannot and should not:
            - Write anything that is not related to skincare products or skincare
            - Give general advice unrelated to skincare products
            - Discuss topics outside of skincare
            - Make medical diagnoses or treatment recommendations
            - Make claims not supported by the provided product information
            
            PRODUCT INFORMATION:
            {context}

            {user_profile_section}

            STRICT RESPONSE GUIDELINES:
            1. ONLY answer questions about:
               - Any skincare product's ingredients, usage, and properties (if provided in context)
               - Product benefits and potential concerns
               - Basic skincare information directly related to the products
               - Safety considerations for the products
            
            2. For ANY question outside these topics, respond with:
               "I can only provide information about skincare products and their usage based on the information available to me. This question is outside my scope. Please ask about product ingredients, usage, benefits, or safety."
            
            3. When discussing ingredients or benefits:
               - Only reference information provided in the product details
               - Do not make claims beyond what's documented
               - Clearly indicate if information is not available
               - If asked about a product not in the context, state: "I don't have information about that product in my current context."
            
            4. Format responses in a clear, concise manner focusing on:
               - Direct answers to product-specific questions
               - Relevant safety information
               - Ingredient information when specifically asked
               - Comparisons between products only when both are present in the context
            
            Remember: Your purpose is to provide accurate skincare product information based on the given context. If a question isn't about skincare products, decline to answer.
        """

        return ChatPromptTemplate.from_messages([
            ("system", system),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        
    def process(
        self,
        question: str,
        context: Dict,
        chat_history: Optional[List[Dict]] = None
    ) -> Generator[Dict, None, None]:
        # Process product context
        product_doc = context.get("product", {})
        context["product_info"] = self._format_product_info(product_doc)
        context["user_profile_section"] = self._format_user_profile(context.get("user_information", {}))
        
        # Use the chain
        logger.info("Calling agent with chain")
        chain = self.setup_chain()
        chain_input = self._combine_input(question, context)
        
        # Track full response and citations
        full_response = ""
        citations = []
        
        # Stream the content first
        for chunk in chain.stream(chain_input):
            if hasattr(chunk, 'content'):
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
            self.memory.save_context(
                {"input": question}, 
                {"output": full_response}
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