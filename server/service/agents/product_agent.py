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
        system = """You are an expert skincare and cosmetics advisor providing concise, accurate answers about beauty products
        
        PRODUCT INFORMATION:
{context}
        
    INSTRUCTIONS:
        1. Answer directly what the user is asking about this specific product.

        2. <think>
        Use this section to analyze the ingredients, assess safety and efficacy, and consider user-specific factors.
        - What specific ingredients are relevant to this question?
        - How do they relate to the user's skin type and concerns?
        - What scientific evidence supports or contradicts claims about these ingredients?
        - What potential risks exist for this user profile?
        </think>

        3. FORMAT YOUR RESPONSE WITH:
        - Direct answer addressing the specific question first
        - Key relevant product ingredients mentioned in context 
        - Concerns or benefits relevant to the user's profile (if available)
        - Simple, concise language with minimal technical jargon
        - Short paragraphs and natural sentence breaks
        - Any key information in the response should be bolded

        4. IMPORTANT:
            - Base your response entirely on the provided product information
            - When user profile is missing, provide general advice applicable to most skin types
            - Acknowledge information gaps rather than making assumptions
        
        **Current Question:**
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
        
        self.set_memory_key(f"chat_history_{product_id}")
        try:
            context["product_info"] = self._format_product_info(product_doc)
            context["user_profile_section"] = self._format_user_profile(context.get("user_information", {}))
        except Exception as e:
            print(f"Error formatting context: {e}")
        
            # Use the chain with context-based model initialization
        try:
            chain = self.setup_chain(context)
        except Exception as e:
            print(f"Error setting up chain: {e}")
        chain_input = self._combine_input(question, context)
        
        # Track full response and citations
        full_response = ""
        citations = []
        in_think_section = False
        # Stream the content first
        for chunk in chain.stream(chain_input):
            content = chunk.content
            full_response += content
            if chunk.additional_kwargs.get('citations', []):
                chunk_citations = chunk.additional_kwargs.get('citations', [])
                citations.extend(chunk_citations)
            
            # Collect citations from chunk
                        # Check for think section markers
            if '<think>' in content:
                in_think_section = True
                continue
            elif '</think>' in content:
                in_think_section = False
                continue
            elif in_think_section:
                continue
            

            # Check for think section markers
            if '<think>' in content:
                in_think_section = True
                continue
            elif '</think>' in content:
                in_think_section = False
                continue
            elif in_think_section:
                continue
            

                
            if content.strip():
                formatted_chunk = ResponseFormatter.format_chunk(content)
                yield formatted_chunk
                
                # If there are remaining chunks, send those too
                if "remaining_chunks" in formatted_chunk:
                    for chunk in formatted_chunk["remaining_chunks"]:
                        yield ResponseFormatter.format_chunk(chunk)
        
        # After content is done, send citations
        if citations:
            yield ResponseFormatter.format_citation('\n\nTo learn more, you can refer to these sources:\n')
            
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
        except Exception as e:
            logger.error(f"Error saving to memory: {str(e)}")
        
    def _format_product_info(self, product_doc: Dict) -> str:
        """Format product information for the prompt"""
        metadata = product_doc.get("metadata", {})
        
        # Extract product details
        product_name = metadata.get("product", "")
        brand_name = metadata.get("brand", "")
        sections = []
        sections.append(f"PRODUCT: {brand_name} {product_name}")
        
        # Parse the page content to extract structured information
        ingredients = []
        benefits = []
        concerns = []
        notable_ingredients = []
        where_it_from = ""
        # Extract information from content
        if metadata:
            # Extract ingredients
            if metadata.get("ingredients", ""):
                ingredients = metadata.get("ingredients", "")
                sections.append("ALL INGREDIENTS:\n• " + "\n• ".join(ingredients))
                
            
            # Extract benefits
            if metadata.get("benefits", ""):
                benefits = metadata.get("benefits", "")
                sections.append("BENEFITS:\n• " + "\n• ".join(benefits))
            
            # Extract concerns
            if metadata.get("concerns", ""):
                concerns = metadata.get("concerns", "")
                sections.append("CONCERNS:\n• " + "\n• ".join(concerns))
                
            if metadata.get("notable_ingredients", ""):
                notable_ingredients = metadata.get("notable_ingredients", "")
                sections.append("KEY INGREDIENTS:\n• " + "\n• ".join(notable_ingredients))
                
            if metadata.get("where_it_from", ""):
                where_it_from = metadata.get("where_it_from", "")
                sections.append(f"ORIGIN: {where_it_from}")
        
        return "\n\n".join(sections)
        
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