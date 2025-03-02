import re
from langchain_community.chat_models import ChatPerplexity
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_together import ChatTogether
from langchain_together.embeddings import TogetherEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from pinecone import Pinecone, ServerlessSpec
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from uuid import uuid4
from datetime import datetime
from service.s3_client import get_s3_client
from langchain_google_genai import ChatGoogleGenerativeAI
from duckduckgo_search import DDGS
from typing import Generator, AsyncGenerator, Dict, Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from service.context_builder import get_initial_context
from service.agents.coordinator import AgentCoordinator
from service.embeddings import pinecone_vector_store
from .model_service import llm
import asyncio
import json
from .chat_service import ChatService
from .context_builder import ContextBuilder
import logging
from .utils.response_formatter import ResponseFormatter, MessageType

duckduckgo = DDGS(timeout=20)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY  = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "product-buddy"
FOLDER_NAME = "chats"
        
api_key = os.getenv("PERPLEXITY_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

s3_client = get_s3_client()

# Initialize coordinator
coordinator = AgentCoordinator()

class ProductChat:
    def __init__(self):
        self.chat_service = ChatService()
        self.context_builder = ContextBuilder()
        self.agent_coordinator = AgentCoordinator()

    def _create_welcome_message(self, product_metadata: dict) -> str:
        """
        Creates a detailed welcome message with product information including subtitle, benefits, concerns, and ingredients.
        """
        product_name = product_metadata.get("product")
        brand_name = product_metadata.get("brand")
        
        # Create subtitle parts
        subtitle_parts = []
        if product_metadata.get("where_it_from") and product_metadata.get("where_it_from") != "Unknown":
            subtitle_parts.append(f"A product of {product_metadata.get('where_it_from')}")
        
        if product_metadata.get("notable_ingredients") and product_metadata.get("notable_ingredients") != "Unknown":
            notable_ingredients = product_metadata.get("notable_ingredients")
            if isinstance(notable_ingredients, list) and notable_ingredients:
                subtitle_parts.append(f"with {', '.join(notable_ingredients[:3])}")
        
        subtitle = " ".join(subtitle_parts) if subtitle_parts else ""
        
        # Format product details sections
        benefits = product_metadata.get("benefits", [])
        benefits_text = "\n".join([f"• {benefit}" for benefit in benefits]) if benefits else "No specific benefits listed"
        
        concerns = product_metadata.get("concerns", [])
        concerns_text = "\n".join([f"• {concern}" for concern in concerns]) if concerns else "No specific concerns listed"
        
        notable_ingredients = product_metadata.get("notable_ingredients", [])
        ingredients_text = "\n".join([f"• {ingredient}" for ingredient in notable_ingredients]) if notable_ingredients else "No notable ingredients listed"
        
        # Construct the welcome message
        welcome_msg = f"""Hi! I am your personalized skincare buddy. I'm here to help you with {product_name} by {brand_name}.

{subtitle}

**Key Product Information:**

**Benefits:**
{benefits_text}

**Concerns Addressed:**
{concerns_text}

**Notable Ingredients:**
{ingredients_text}

How can I assist you today?"""

        return welcome_msg

    def initialize_chat(self, cookie_id: str, product_id: str) -> Dict:
        """Initialize a new chat session for a product."""
        try:
            # Get chat history and context
            chat_data = self.chat_service.get_chat(cookie_id, product_id)
            context = self.context_builder.get_context(cookie_id, product_id)
            # Combine chat data with context
            product_name = context.get('product').get('metadata').get("product")
            brand_name = context.get('product').get('metadata').get("brand")
            welcome_msg = self._create_welcome_message(context.get('product').get('metadata'))
            messages = [{
                        "content": welcome_msg,
                        "role": "assistant",
                        "id": "welcome_message",
                        "timestamp": datetime.utcnow().isoformat()
                    }]
            chat_data = {
                    "product_name": product_name,
                    "brand_name": brand_name,
                    "image_url": context.get('product').get('metadata').get("image_url"),
                    "chat_history": messages,
                    "product_id": product_id,
                    "preloaded_context": context
                }
            self.chat_service.save_chat(cookie_id, product_id, chat_data)    
            
            return chat_data
            
        except Exception as e:
            raise

    def handle_message(
        self,
        cookie_id: str,
        product_id: str,
        message: str
    ) -> Generator[Dict, None, None]:
        """Handle an incoming chat message."""
        try:
            # Save the user's message
            chat_data = self.chat_service.get_chat(cookie_id, product_id)
            chat_data["chat_history"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.utcnow().isoformat()
            })
            self.chat_service.save_chat(cookie_id, product_id, chat_data)
            
            context = chat_data.get("preloaded_context")
            
            # Get or create context
            if not context:
                context = self.context_builder.get_context(cookie_id, product_id)
            
            # Pass through formatted chunks from agent
            accumulated_response = ""
            accumulated_citations = ""
            for chunk in self.agent_coordinator.process_question(
                question=message,
                context=context,
                chat_history=chat_data.get("chat_history", [])
            ):
                if chunk["type"] == MessageType.CHUNK.value:
                    accumulated_response += chunk["content"]
                elif chunk["type"] == MessageType.CITATION.value:
                    accumulated_citations += chunk["content"]
                yield chunk
            
            # Save the complete response with citations
            full_response = accumulated_response + accumulated_citations
            cleaned_response = re.sub(r'<think>[\s\S]*?</think>', '', full_response, flags=re.DOTALL).strip()
            chat_data["chat_history"].append({
                "role": "assistant",
                "content": cleaned_response,
                "timestamp": datetime.utcnow().isoformat()
            })
            self.chat_service.save_chat(cookie_id, product_id, chat_data)
            
            yield ResponseFormatter.format_done()
            
        except Exception as e:
            raise

