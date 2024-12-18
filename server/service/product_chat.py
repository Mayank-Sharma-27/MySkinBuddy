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
from langchain.memory import ConversationBufferMemory
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
index = pc.Index("product-buddy")
parser = StrOutputParser()
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

memory = ConversationBufferMemory()
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

def get_initial_context(product_name: str, brand_name: str):
    """
    Get initial context for a product including its details and all its ingredients
    """
    print(f"\n🔍 Getting initial context for {product_name} by {brand_name}")
    
    try:
        # Get product document
        product_filter = {
            "brand": brand_name.lower(),
            "product": product_name.lower(),
            "type": "product"
        }
        
        product_docs = pinecone_vector_store.similarity_search(
            "",  # Empty query to get exact match
            k=1,
            filter=product_filter
        )
        
        if not product_docs:
            raise ValueError(f"Product not found: {product_name} by {brand_name}")
        
        product_doc = product_docs[0]
        
        # Convert Document object to serializable dict
        context = {
            "product": {
                "page_content": product_doc.page_content,
                "metadata": product_doc.metadata
            }
        }
        return context
        
    except Exception as e:
        print(f"❌ Error getting initial context: {str(e)}")
        raise

def initialize_chat(cookie_id: str, product_name: str, brand_name: str, image_url: str) -> str:
    """Initialize a new chat session for a specific product"""
    chat_id = str(uuid4())
    print(f"Initializing chat for - Product: '{product_name}', Brand: '{brand_name}'")
    
    try:
        # Get initial context
        initial_context = get_initial_context(product_name, brand_name)
        
        # Create chat session data
        chat_data = {
            "product": product_name,
            "brand": brand_name,
            "image_url": image_url,
            "created_time": datetime.utcnow().isoformat(),
            "last_updated_time": datetime.utcnow().isoformat(),
            "chat_history": [],
            "preloaded_context": initial_context
        }
        
        # Save to S3
        save_chat(cookie_id, chat_id, chat_data)
        
        print(f"Chat initialized with ID: {chat_id}")
        return chat_id
    except Exception as e:
        print(f"Error initializing chat: {str(e)}")
        raise

def handle_chat_message(cookie_id: str, chat_id: str, user_question: str):
    """Handle a chat message and return the response"""
    try:
        # Get chat data from S3
        chat_data = get_chat(cookie_id, chat_id)
        
        # Generate response
        accumulated_response = ""
        for chunk in generate_response(chat_data, user_question):
            if isinstance(chunk, dict):
                content = chunk.get('content', '')
            else:
                content = str(chunk)
                
            accumulated_response += content
            yield content
        
        # Update chat history
        chat_data["chat_history"].append({
            "question": user_question,
            "response": accumulated_response
        })
        chat_data["last_updated_time"] = datetime.utcnow().isoformat()
        save_chat(cookie_id, chat_id, chat_data)     
    except Exception as e:
        print(f"Error handling message: {str(e)}")
        raise

def get_chat_history(cookie_id: str, chat_id: str):
    """Get chat history from S3"""
    try:
        chat_data = get_chat(cookie_id, chat_id)
        return chat_data
    except Exception as e:
        print(f"Error getting chat history: {str(e)}")
        raise
def get_search_results(user_question: str, context: str, chat_history: str = ""):
    try:
        search_prompt = """Based on the following information, generate ONE specific search query to find additional relevant information.
        
        Context from product: {context}
        Previous conversation: {chat_history}
        Current question: {user_question}
        
        Requirements:
        1. For product comparison or alternative questions:
           - Include key ingredients from the original product in the search
           - Include the product category (e.g., serum, moisturizer, mask)
           - Include price comparison terms if mentioned
        2. Focus ONLY on finding information that is NOT already covered in the context or chat history
        3. Make the query specific and targeted
        4. Include the product type and main ingredients, but avoid the brand name
        5. Only output the search query itself - no explanations
        6. If the question can be fully answered with existing context, output: "NO_SEARCH_NEEDED"
        """
        
        try:
            # Generate the search query using the model
            model_search = model.invoke(search_prompt.format(
                context=context,
                user_question=user_question,
                chat_history=chat_history
            ))
            search_query = model_search.content.strip().replace("```", "").replace('"', '')
        except Exception as e:
            print(f"⚠️ Model error, using fallback search: {str(e)}")
            # Fallback to basic keyword search
            keywords = user_question.lower().split()
            search_query = " ".join([w for w in keywords if len(w) > 3])
        
        if search_query == "NO_SEARCH_NEEDED":
            print("ℹ️ No additional search needed - sufficient context available")
            return ""
        
        print(f"🔎 Generated search query: {search_query}")
        
        # Get search results from DuckDuckGo with retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Convert generator to list so we can use it multiple times
                search_results = list(duckduckgo.text(search_query, max_results=5))
                
                
                # Now we can safely use search_results multiple times
                # Both for URL extraction and formatting
                return search_results
                
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"⚠ Search error after {max_retries} attempts: {str(e)}")
                    return "Unable to fetch search results at this time."
                time.sleep(1)
                
    except Exception as e:
        print(f"❌ Critical error in get_search_results: {str(e)}")
        return "Unable to process search request at this time."
        return "Unable to fetch search results at this time."
    
def extract_urls_from_search_results(search_results) -> list:
    """Extract URLs from search results
    
    Args:
        search_results: List of dictionaries containing search results with 'href' URLs
        
    Returns:
        list: List of URLs from the search results
    """   
    print("\n=== URL Extraction Start ===")
    print(f"Input search_results type: {type(search_results)}")
    print(f"Input search_results: {search_results}")
    
    # Handle if search_results is None or not a list
    if not search_results or not isinstance(search_results, list):
        print("❌ Search results is empty or not a list")
        return []
        
    # Extract URLs, ensuring each result is a dictionary
    urls = [result['href'] for result in search_results 
            if isinstance(result, dict) and 'href' in result]
    
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
        formatted_history = "\n".join([
            f"Previous Question: {exchange['question']}\n"
            f"Previous Answer: {exchange['response']}\n"
            for exchange in chat_history[-3:]  # Keep last 3 exchanges for context
        ])
        print(formatted_history)
        search_results = get_search_results(
            user_question=user_question, 
            context=context,
            chat_history=formatted_history
        )
         # Debug print
        # Extract sources before sending to model
        sources = extract_urls_from_search_results(search_results)
        print(f"Debug - Sending sources first: {sources}")
        search_result = "\n\n".join([
                    f"Product Information {i + 1}:\n"
                    f"Title: {result['title']}\n"
                    f"Description: {result['body']}\n"
                    f"URL: {result['href']}"
                    for i, result in enumerate(search_results)
                    if result['body'].strip()
                ])
        # Debug the full prompt being sent to Perplexity
        full_prompt = prompt.format(
            context=context,
            question=user_question,
            chat_history=formatted_history,
            product_name=chat_session["product"],
            brand_name=chat_session["brand"],
            search_results=search_result
        )
        
        # Then start streaming content
        
        for chunk in model.stream(full_prompt):
            
            content = chunk.content
            
            yield {
                "content": content
                }

        yield {
            "content": ", ".join(sources) if sources else ""
        }
    except Exception as e:
        print(f"\n❌ Error generating response: {str(e)}")
        yield {
            "type": "error",
            "content": str(e),
            "sources": []
        }
