from langchain_community.chat_models import ChatPerplexity
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_together.embeddings import TogetherEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_openai.embeddings import OpenAIEmbeddings
import boto3
import json
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
import time
from pinecone import Pinecone, ServerlessSpec
from langchain_core.memory import ConversationBufferMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import re
from uuid import uuid4
from datetime import datetime
from service.s3_client import get_s3_client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchResults
from duckduckgo_search import DDGS
import google.api_core.exceptions
from service.chat_service import get_chat, save_chat;
from typing import Generator
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper



duckduckgo = DDGS(timeout=20)
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY  = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "product-buddy"
FOLDER_NAME = "chats"
BATCH_SIZE = 100
        
system = """
As an expert in skin care products, your task is to embody the persona of the {product_name} created by {brand_name}. Maintain a friendly and concise tone throughout the conversation.

### Guidelines:
- Provide straightforward answers to user inquiries.
- Conduct comparative analyses of products and ingredients.
- Only disclose specific prices upon user requests.
- Utilize **ingredient** formatting to highlight key components.
- Address skin concerns with quick yes/no responses and key ingredients.
- Include product prices and shared ingredients when making product comparisons.
- Suggest alternative products by specifying them with prices and accompanying links.
- Offer direct responses without unnecessary elaboration.

Your information:
{context}

Previous conversation:
{chat_history}

Current question: {question}
   
"""

human = """
User Question: {question}
"""



## Find percentage of ingredients

prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

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

memory = ConversationBufferMemory(return_messages=True)
s3_client = get_s3_client()
pinecone_vector_store = PineconeVectorStore(index=index, embedding=embeddings)


def get_search_results(product_name: str, brand_name: str):
    max_retries = 3
    try:
        search_query = f"{product_name} by {brand_name} skincare information"
        print(f"Search query: {search_query}")
        for attempt in range(max_retries):
            try:
                #search_results = search_tool.results(search_query, 5)
                return "search_results"  # Exit the loop if successful
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"⚠ Search error after {max_retries} attempts: {str(e)}")
                    return "Unable to fetch search results at this time."
                
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"⚠ Search error after {max_retries} attempts: {str(e)}")
                    return "Unable to fetch search results at this time."
                
    except Exception as e:
        print(f"Error getting search results: {str(e)}")
        return "Unable to fetch search results at this time."
    
def extract_urls_from_search_results(search_results) -> list:
    """Extract URLs from search results
    
    Args:
        search_results: List of dictionaries containing search results with 'href' URLs
        
    Returns:
        list: List of URLs from the search results
    """   
    print(f"Input search_results type: {type(search_results)}")
    print(f"Input search_results: {search_results}")
    
    # Handle if search_results is None or not a list
    if not search_results or not isinstance(search_results, list):
        print("❌ Search results is empty or not a list")
        return []
        
    # Extract URLs, ensuring each result is a dictionary
    urls = [result['link'] for result in search_results 
            if isinstance(result, dict) and 'link' in result]
    
    print(f"✅ Extracted URLs: {urls}")
    print("=== URL Extraction End ===\n")
            
    return urls

def generate_response(chat_session: dict, user_question: str):
    print("\n⌛ Generating response...")
    
    try:
        # Get the product context from preloaded context
        product_doc = chat_session["preloaded_context"]["product"]
        product_info = product_doc["page_content"]
        
        # Extract ingredients from the product info
        ingredients_start = product_info.find("Ingredients :") + len("Ingredients :")
        product_details = product_info[:ingredients_start].strip()
        ingredients_list = product_info[ingredients_start:].strip()
        
        # Build the context string with separated product info and ingredients
        context = (
            f"PRODUCT INFO:\n{product_details}\n\n"
            f"INGREDIENTS:\n{ingredients_list}\n\n"
        )
        
        # Format chat history with clear question-answer pairs
        chat_history = chat_session.get("chat_history", [])
        #formatted_history = "\n".join([
        #    f"Previous Question: {exchange['question']}\n"
        #    f"Previous Answer: {exchange['response']}\n"
        #    for exchange in chat_history[-3:]  # Keep last 3 exchanges for context
        #])
        product_name = chat_session["preloaded_context"]['product']["metadata"]["product"]
        brand_name = chat_session["preloaded_context"]['product']["metadata"]["brand"]

        full_prompt = prompt.format(
            context=context,
            question=user_question,
            chat_history=[],
            product_name= product_name,
            brand_name= brand_name
        )
        print(f"Full prompt: {full_prompt}")
        for chunk in model.stream(full_prompt):
            
            content = chunk.content
            
            yield {
                "content": content
                }
    except Exception as e:
        print(f"\n❌ Error generating response: {str(e)}")
        yield {
            "type": "error",
            "content": str(e),
            "sources": []
        }
        
def get_chat_history(cookie_id: str, chat_id: str):
    """Get chat history from S3"""
    try:
        chat_data = get_chat(cookie_id, chat_id)
        return chat_data
    except Exception as e:
        print(f"Error getting chat history: {str(e)}")
        raise        