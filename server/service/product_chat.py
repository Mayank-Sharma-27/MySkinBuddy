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
from service.chat_service import get_chat, save_chat, initialize_agents_data;
from typing import Generator
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from service.generate_chat_response import generate_response 
from service.context_builder import get_initial_context
from service.agents.coordinator import AgentCoordinator

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

def initialize_chat(cookie_id: str, product_id: str) -> dict:
    """
    Initialize or get existing chat session for a specific product
    """
    try:
        try:
            # Try to get existing chat
            chat_data = get_chat(cookie_id, product_id)
            chat_data_to_return = {
                "product_id": product_id,
                "product_name": chat_data["product_name"],
                "brand_name": chat_data["brand_name"],
                "image_url": chat_data["image_url"],
                "chat_history": chat_data["chat_history"],
            }
            return chat_data_to_return
        except:
            # If no existing chat, create new one
            initial_context = get_initial_context(product_id)
            product_name = initial_context['product']["metadata"]["product"]
            brand_name = initial_context['product']["metadata"]["brand"]
            image_url = initial_context['product']['metadata']['image_url']
            source_url = initial_context['product']['metadata']['source_url']
            
            # Create chat session data
            chat_data = {
                "product_id": product_id,
                "product_name": product_name,
                "brand_name": brand_name,
                "image_url": image_url,
                "chat_history": [],
                "preloaded_context": initial_context,
            }
            
            # Save chat data
            save_chat(cookie_id, product_id, chat_data)
            
            chat_data_to_return = {
                "product_id": product_id,
                "product_name": product_name,
                "brand_name": brand_name,
                "image_url": image_url,
                "chat_history": [],
            }
            return chat_data_to_return
            
    except Exception as e:
        print(f"Error initializing chat: {str(e)}")
        raise

async def handle_chat_message(cookie_id: str, product_id: str, user_question: str) -> Generator[str, None, None]:
    """Handle a chat message and return the response"""
    try:
        # Get chat data
        chat_data = get_chat(cookie_id, product_id)
        if not chat_data:
            raise Exception("Chat not found")
            
        # Generate response using coordinator
        accumulated_response = ""
        async for chunk in coordinator.process_question(
            question=user_question,
            context=chat_data,
            chat_history=chat_data["chat_history"]
        ):
            accumulated_response += chunk
            yield chunk
        
        # Update chat history
        chat_data["chat_history"].append({
            "role": "user",
            "content": user_question,
            "timestamp": datetime.utcnow().isoformat()
        })
        chat_data["chat_history"].append({
            "role": "assistant",
            "content": accumulated_response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        chat_data["last_updated_time"] = datetime.utcnow().isoformat()
        save_chat(cookie_id, product_id, chat_data)
        
    except Exception as e:
        print(f"Error handling message: {str(e)}")
        raise

