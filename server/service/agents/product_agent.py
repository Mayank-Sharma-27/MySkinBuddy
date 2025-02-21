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
        [Cosmetics Expert Protocol v2.1]
         **Role**: Top-tier dermatologist & cosmetic expert 
         Context|{context} with {user_profile_section}
        
        Response Protocol:
        1. Safety First: Highlight risks using [⚠️] before any concern
        2. Efficacy Evidence: Cite ≥1 clinical study from context 
        3. Profile Match: Use [✅] when aligning with profile data
        4. Output: 55-65 tokens via:
            - Concise Benefit/Risk Summary (30-40 tokens)
        - Key Ingredients Analysis (20-25 tokens)
        - Climate Consideration if relevant (10-15 tokens)
            
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
        in_think_section = False
        # Stream the content first
        for chunk in chain.stream(chain_input):
            content = chunk.content
            full_response += content
            chunk_citations = chunk.additional_kwargs.get('citations', [])
            
            # Collect citations from chunk
            
            if chunk_citations:
                citations.extend(chunk_citations)
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
            logger.info("Saving to memory done")
        except Exception as e:
            logger.error(f"Error saving to memory: {str(e)}")
        
    def _format_product_info(self, product_doc: Dict) -> str:
        """Format product information for the prompt"""
        content = product_doc.get("page_content", "")
        metadata = product_doc.get("metadata", {})
        
        # Extract product details
        product_name = metadata.get("product", "")
        brand_name = metadata.get("brand", "")
        
        # Parse the page content to extract structured information
        ingredients = []
        benefits = []
        concerns = []
        
        # Extract information from content
        if content:
            # Extract ingredients
            if "Notable Ingredients:" in content:
                ingredients_section = content.split("Notable Ingredients:")[1].split(".")[0]
                ingredients = [i.strip() for i in ingredients_section.split(",")]
            
            # Extract benefits
            if "Benefits:" in content:
                benefits_section = content.split("Benefits:")[1].split(".")[0]
                benefits = [b.strip() for b in benefits_section.split(",")]
            
            # Extract concerns
            if "Concerns:" in content:
                concerns_section = content.split("Concerns:")[1].split(".")[0]
                concerns = [c.strip() for c in concerns_section.split(",")]
        
        # Format ingredients, benefits, and concerns
        ingredients_text = ('• ' + '\n• '.join(ingredients)) if ingredients else 'No ingredient information available'
        benefits_text = ('• ' + '\n• '.join(benefits)) if benefits else 'No benefits information available'
        concerns_text = ('• ' + '\n• '.join(concerns)) if concerns else 'No concerns information available'
        
        # Format the information without line breaks in f-string
        formatted_info = f"**Product Details:**\n• Brand: {brand_name}\n• Product: {product_name}\n\n**Key Ingredients:**\n{ingredients_text}\n\n**Known Benefits:**\n{benefits_text}\n\n**Potential Concerns:**\n{concerns_text}"
        
        return formatted_info
        
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