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

def initialize_chat(product_name: str, brand_name: str):
    """
    Initialize a new chat session for a specific product
    """
    chat_id = str(uuid4())
    print(f"Initializing chat for - Product: '{product_name}', Brand: '{brand_name}'")
    
    try:
        active_chats[chat_id] = {
            "product": product_name,
            "brand": brand_name,
            "chat_history": []
        }
        print(f"Chat initialized with ID: {chat_id}")
        return chat_id
    except Exception as e:
        print(f"Error initializing chat: {str(e)}")
        raise

def handle_chat_message(chat_id: str, user_question: str):
    """
    Handle a chat message and return the response
    """
    if chat_id not in active_chats:
        raise ValueError("Chat session not found")
    
    chat_session = active_chats[chat_id]
    
    if user_question.lower() == "exit":
        # TODO: Save chat history to S3 when user is signed in
        del active_chats[chat_id]
        return "👋 Thanks for chatting! Have a great day!"
    
    try:
        response = generate_response(chat_session, user_question)
        
        # Store in chat history
        chat_session["chat_history"].append({
            "question": user_question,
            "response": response
        })
        
        return response
        
    except Exception as e:
        print(f"Error handling message: {str(e)}")
        raise

# We'll implement these functions next
def generate_response(chat_session: dict, user_question: str):
    print("\n⌛ Analyzing product information...")
    print(f"Debug - Searching for: Product='{chat_session['product']}', Brand='{chat_session['brand']}'")
    
    try:
        # Get product context
        product_filter = get_product_filter(chat_session["product"], chat_session["brand"])
        retriever = pinecone_vector_store.as_retriever(
            search_kwargs={
                "k": 20,
                "filter": product_filter
            }
        )
        
        context_docs = retriever.invoke(user_question.lower())
        print(f"\nFound {len(context_docs)} relevant documents")
        
        # Debug: Print all retrieved documents
        print("\n🔍 Retrieved Documents:")
        for i, doc in enumerate(context_docs):
            print(f"\nDocument {i + 1}:")
            print(f"Content: {doc.page_content}")
            print(f"Metadata: {doc.metadata}")
        
        # Organize context by type
        ingredients = []
        benefits = []
        
        for doc in context_docs:
            metadata = doc.metadata
            chunk_text = doc.page_content
            
            if metadata.get("type") == "ingredient":
                ingredients.append(chunk_text)
            elif metadata.get("type") == "benefits":
                benefits.append(chunk_text)
        
        context = (
            f"INGREDIENTS:\n{'; '.join(ingredients)}\n\n"
            f"BENEFITS:\n{'; '.join(benefits)}\n\n"
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
        
        # Debug: Print final prompt
        print("\n📋 Final Prompt:")
        print(prompt.format(
            context=context,
            question=user_question,
            chat_history=formatted_history,
            product_name=chat_session["product"],
            brand_name=chat_session["brand"]
        ))
        
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
        
        #response_text = str(response.content) if hasattr(response, 'content') else str(response)
        
        # Debug: Print final response
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
