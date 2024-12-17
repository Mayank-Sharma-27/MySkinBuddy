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


load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY  = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "product-buddy"
FOLDER_NAME = "chats"
BATCH_SIZE = 100
        
system = """
You are the {product_name} by {brand_name}. Be friendly but concise. Responses must be 2-3 sentences long.

### Guidelines:
- **Skin Concern Questions**: Answer with a quick yes/no, highlight 1-2 key ingredients, and give a brief reason.
- **Ingredient/Product Comparison**: Focus on similarities or differences and effects.
- **General Questions**: Direct answers only. No unnecessary details.

Your information:
{context}

Previous conversation:
{chat_history}

Remember: Be concise, friendly, and factual. Answer as the product.
"""

human = """
User Question: {question}
"""



## Find percentage of ingredients

prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

api_key = os.getenv("PERPLEXITY_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = ChatPerplexity(api_key =api_key,
                     model= "llama-3.1-sonar-small-128k-online",
                     streaming=True,
                     temperature= 2)
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
        
        context = {
            "product": product_doc
        }
        return context
        
    except Exception as e:
        print(f"❌ Error getting initial context: {str(e)}")
        raise

def initialize_chat(cookie_id: str, product_name: str, brand_name: str) -> str:
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
            "created_time": datetime.utcnow().isoformat(),
            "last_updated_time": datetime.utcnow().isoformat(),
            "chat_history": [],
            "preloaded_context": initial_context
        }
        
        # Save to S3
        s3_key = f"cookies/{cookie_id}/{chat_id}.json"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=json.dumps(chat_data),
            ContentType='application/json'
        )
        
        print(f"Chat initialized with ID: {chat_id}")
        return chat_id
    except Exception as e:
        print(f"Error initializing chat: {str(e)}")
        raise

def handle_chat_message(cookie_id: str, chat_id: str, user_question: str):
    """Handle a chat message and return the response"""
    try:
        # Get chat data from S3
        s3_key = f"cookies/{cookie_id}/{chat_id}.json"
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
        chat_data = json.loads(response['Body'].read().decode('utf-8'))
        
        # Generate response
        response_stream = generate_response(chat_data, user_question)
        
        accumulated_response = ""
        for chunk in response_stream:
            if chunk:
                accumulated_response += chunk
                yield chunk
        
        # Update chat history
        chat_data["chat_history"].append({
            "question": user_question,
            "response": accumulated_response
        })
        chat_data["last_updated_time"] = datetime.utcnow().isoformat()
        
        # Save updated chat data
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=json.dumps(chat_data),
            ContentType='application/json'
        )
        
    except Exception as e:
        print(f"Error handling message: {str(e)}")
        raise

def get_chat_history(cookie_id: str, chat_id: str):
    """Get chat history from S3"""
    try:
        s3_key = f"cookies/{cookie_id}/{chat_id}.json"
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
        chat_data = json.loads(response['Body'].read().decode('utf-8'))
        return chat_data
    except Exception as e:
        print(f"Error getting chat history: {str(e)}")
        raise

def generate_response(chat_session: dict, user_question: str):
    print("\n⌛ Generating response...")
    
    try:
        # Check if the question is about similar products
        #if any(phrase in user_question.lower() for phrase in ["similar products", "like this", "comparable", "alternative"]):
            #response = generate_similar_products_response(chat_session["context"]["product"])
            #yield response
            #return
        
        # Original response generation logic continues...
        context_docs = [chat_session["context"]["product"]] + chat_session["context"]["ingredients"]
        
        # Organize context by type
        ingredients = []
        
        for doc in context_docs:
            if doc.metadata["type"] == "ingredient":
                ingredients.append(doc.page_content)
            elif doc.metadata["type"] == "product":
                product_info = doc.page_content
        
        context = (
            f"PRODUCT INFO:\n{product_info}\n\n"
            f"INGREDIENTS:\n{'; '.join(ingredients)}\n\n"
        )
        
        # Debug: Print organized context
        print("\n📝 Organized Context:")
        print(context)
        
        chat_history = chat_session.get("chat_history", [])
        formatted_history = "\n".join([
            f"Question: {exchange['question']}\nAnswer: {exchange['response']}"
            for exchange in chat_history[-3:]
        ])
        
        # Debug: Print chat history
        print("\n💬 Chat History:")
        print(formatted_history)
        
        # Generate response
        response_stream = model.stream(
            prompt.format(
                context=context,
                question=user_question,
                chat_history=formatted_history,
                product_name=chat_session["product"],
                brand_name=chat_session["brand"]
            )
        )
        
        for chunk in response_stream:
            if hasattr(chunk, 'content'):
                yield chunk.content
            else:
                yield str(chunk)    
            
    except Exception as e:
        print(f"\n❌ Error generating response: {str(e)}")
        error_msg = "I apologize, but I'm having trouble analyzing this product right now. Please try asking your question again."
        raise Exception(error_msg) from e

def save_chat_history(user_id: str, chat_session: dict):
    """
    Save chat history to S3 for signed-in users
    """
    # TODO: Implement S3 storage
    pass
