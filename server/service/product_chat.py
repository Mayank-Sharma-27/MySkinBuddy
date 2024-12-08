from langchain_together import ChatTogether
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
BUCKET_NAME = "skinsortdata"
FOLDER_NAME = "products"
BATCH_SIZE = 100
        
template = """
You are the {product_name} by {brand_name}. Be friendly but concise. Responses must be 2-3 sentences long.

### Guidelines:
- **Skin Concern Questions**: Answer with a quick yes/no, highlight 1-2 key ingredients, and give a brief reason.
- **Ingredient/Product Comparison**: Focus on similarities or differences and effects.
- **General Questions**: Direct answers only. No unnecessary details.

Your information:
{context}

Previous conversation:
{chat_history}

User Question: {question}

Remember: Be concise, friendly, and factual. Answer as the product.
"""

## Find percentage of ingredients

prompt = ChatPromptTemplate.from_template(template)

api_key = os.getenv("TOGETHER_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = ChatTogether(api_key =api_key,
                     model= "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                     streaming=True,
                     callbacks=[StreamingStdOutCallbackHandler()])
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("skin-buddy")
parser = StrOutputParser()
embeddings = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-32k-retrieval")

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
        
        # Extract ingredient names from product document
        ingredients_text = product_doc.page_content
        ingredients_section = ingredients_text.split("Ingredients: ")[-1].strip(".")
        ingredient_names = [ing.strip() for ing in ingredients_section.split(",")]
        
        # Get ingredient documents
        ingredient_docs = []
        for ingredient_name in ingredient_names:
            ingredient_filter = {
                "ingredient_name": ingredient_name.lower(),
                "type": "ingredient"
            }
            
            matching_docs = pinecone_vector_store.similarity_search(
                "",  # Empty query to get exact match
                k=1,
                filter=ingredient_filter
            )
            
            if matching_docs:
                ingredient_docs.append(matching_docs[0])
        
        # Organize context
        context = {
            "product": product_doc,
            "ingredients": ingredient_docs
        }
        
        print(f"✅ Found product and {len(ingredient_docs)} ingredients")
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

def generate_similar_products_response(product_doc):
    """
    Generate a formatted response for similar products
    """
    try:
        similar_products = find_similar_products(product_doc)
        
        if not similar_products:
            return "I couldn't find any products with similar ingredients."
            
        # Format similar products information
        similar_products_text = "Here are some similar products:\n\n"
        for i, prod in enumerate(similar_products[:3], 1):  # Show top 3
            similarity_percentage = int(prod["similarity_score"] * 100)
            shared_ingredients_text = ", ".join(prod["shared_ingredients"][:3])  # Show first 3 shared ingredients
            similar_products_text += (
                f"{i}. {prod['product']} by {prod['brand']}\n"
                f"   • {similarity_percentage}% ingredient match\n"
                f"   • Key shared ingredients: {shared_ingredients_text}\n\n"
            )
        
        return similar_products_text
        
    except Exception as e:
        print(f"Error generating similar products response: {str(e)}")
        return "I apologize, but I'm having trouble finding similar products right now."

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
