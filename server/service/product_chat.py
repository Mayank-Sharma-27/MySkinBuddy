from langchain_community.chat_models import ChatPerplexity
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_together.embeddings import TogetherEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
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
from service.generate_chat_response import generate_response 
from service.context_builder import get_initial_context
from service.agents.coordinator import AgentCoordinator
from service.cookie_service import CookieService
import asyncio
import json
from .chat_service import ChatService
from .context_builder import ContextBuilder

duckduckgo = DDGS(timeout=20)

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY  = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "product-buddy"
FOLDER_NAME = "chats"
BATCH_SIZE = 100
        
api_key = os.getenv("PERPLEXITY_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
    max_tokens=None,
    timeout=30,
    max_retries=3,
    streaming=True
)
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("product-buddy-google")
parser = StrOutputParser()
embeddings = embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

s3_client = get_s3_client()
pinecone_vector_store = PineconeVectorStore(index=index, embedding=embeddings)

# Initialize coordinator
coordinator = AgentCoordinator()

class ProductChat:
    def __init__(self):
        self.chat_service = ChatService()
        self.context_builder = ContextBuilder()
        self.agent_coordinator = AgentCoordinator()

    def initialize_chat(self, cookie_id: str, product_id: str) -> Dict:
        """Initialize a new chat session for a product."""
        try:
            # Get chat history and context
            chat_data = self.chat_service.get_chat(cookie_id, product_id)
            context = self.context_builder.get_context(cookie_id, product_id)
            
            # Combine chat data with context
            if chat_data:
                chat_data["preloaded_context"] = context
            else:
                chat_data = {
                    "chat_history": [],
                    "product_id": product_id,
                    "preloaded_context": context
                }
            
            return chat_data
            
        except Exception as e:
            raise

    def handle_message(
        self,
        cookie_id: str,
        product_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> Generator[str, None, None]:
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
            
            # Get or create context
            if not context:
                context = self.context_builder.get_context(cookie_id, product_id)
            
            # Process the question through the agent coordinator
            accumulated_response = ""
            for chunk in self.agent_coordinator.process_question(
                question=message,
                context=context,
                chat_history=chat_data.get("chat_history", [])
            ):
                accumulated_response += chunk
                
                # Prepare chunk message
                chunk_message = {
                    "type": "assistant_chunk",
                    "content": chunk
                }
                yield chunk_message
            
            # Save the assistant's complete response
            chat_data["chat_history"].append({
                "role": "assistant",
                "content": accumulated_response,
                "timestamp": datetime.utcnow().isoformat()
            })
            self.chat_service.save_chat(cookie_id, product_id, chat_data)
            
            # Send done message
            yield {"type": "done"}
            
        except Exception as e:
            raise

