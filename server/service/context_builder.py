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
from service.s3_client import get_s3_client

duckduckgo = DDGS(timeout=20)


load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY  = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "product-buddy"
FOLDER_NAME = "chats"
BATCH_SIZE = 100
        
system = """
You are the {product_name} by {brand_name}. Be friendly but concise.:

### Guidelines:
- 
    - Answer the question directly
    - Compare products/ingredients
    - Mention specific prices only if asked by the user.
    - Use **ingredient** formatting
    - Skin Concerns: Quick yes/no + key ingredients
    - Product Comparisons: Include prices and shared ingredients
    - Alternatives: Specific products with prices and links
    - General: Direct answers only

Your information:
{context}

External research results:
{search_results}

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


s3_client = get_s3_client()
pinecone_vector_store = PineconeVectorStore(index=index, embedding=embeddings)

def normalize_product_name(name):
    name = name.lower()
    
    name = re.sub(r'[^a-z0-9\s]', '', name)
    
    name = ' '.join(name.split())
    
    return name

def get_product_filter(product_name: str, brand_name: str):
    # Debug the original values
    print(f"Debug - Original values: Product='{product_name}', Brand='{brand_name}'")
    
    # Normalize the brand and product names
    brand_name = brand_name.lower().strip()
    product_name = product_name.lower().strip()
    
    # Debug the normalized values
    print(f"Debug - Normalized values: Product='{product_name}', Brand='{brand_name}'")
    
    # Create a simple filter
    return {
        "brand": brand_name,
        "product": product_name
    }
    
# Store active chat sessions
active_chats = {}

def get_initial_context(product_id: str):
    """
    Get initial context for a product including its details and all its ingredients.
    First checks S3 for cached context, if not found fetches from Pinecone and caches it.
    """    
    try:
        # Check if context exists in S3
        s3_key = f"product-context/{product_id}/product_context.json"
        try:
            response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
            context = json.loads(response['Body'].read().decode('utf-8'))
            print(f"✅ Found cached context in S3 for product: {product_id}")
            return context
        except s3_client.exceptions.NoSuchKey:
            print(f"🔍 No cached context found in S3 for product: {product_id}")
            
        # Get product document from Pinecone
        product_filter = {
            "product_id": product_id,
            "type": "product"
        }
        
        product_docs = pinecone_vector_store.similarity_search(
            "",  # Empty query to get exact match
            k=1,
            filter=product_filter
        )
        
        if not product_docs:
            raise ValueError(f"Product not found: {product_id}")
        
        product_doc = product_docs[0]
        # Convert Document object to serializable dict
        context = {
            "product": {
                "page_content": product_doc.page_content,
                "metadata": product_doc.metadata
            }
        }
        
        # Cache the context in S3
        try:
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=json.dumps(context),
                ContentType='application/json'
            )
            print(f"✅ Cached context in S3 for product: {product_id}")
        except Exception as e:
            print(f"⚠️ Failed to cache context in S3: {str(e)}")
            
        return context
        
    except Exception as e:
        print(f"❌ Error getting initial context: {str(e)}")
        raise