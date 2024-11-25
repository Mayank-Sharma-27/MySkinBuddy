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
You are SkinBuddy, a friendly and knowledgeable skincare expert. Provide brief, focused answers.

For yes/no questions (e.g., "Is this good for dry skin?"), use this format:
Answer: [Yes/No]
Key Ingredients: [List 2-3 relevant ingredients]
Reason: [1-2 short sentences]

For all other questions, provide a direct answer in 1-2 sentences, focusing only on the specific information requested.

Product Information:
Product: {product_name}
Brand: {brand_name}

Available Context:
{context}

Previous Conversation:
{chat_history}

User Question: {question}

Remember: Always be concise. No lengthy explanations.
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

def get_product_filter(product_name, brand_name, threshold=85):
    normalized_product = normalize_product_name(product_name)
    normalized_brand = normalize_product_name(brand_name)
    print(f"Debug - Searching for: Product='{normalized_product}', Brand='{normalized_brand}'")
    return {
        "$and": [
            {"brand": {"$eq": normalized_brand}},
            {"product": {"$eq": normalized_product}}
        ]
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
    """
    Generate a response based on the user's question and product context
    
    Args:
        chat_session: The current chat session containing product info and history
        user_question: The user's question
        
    Returns:
        str: The generated response
    """
    print("\n⌛ Analyzing product information...")
    
    try:
        # Get product context
        product_filter = get_product_filter(chat_session["product"], chat_session["brand"])
        retriever = pinecone_vector_store.as_retriever(
            search_kwargs={
                "k": 20,
                "filter": product_filter
            }
        )
        
        # Get relevant documents
        context_docs = retriever.invoke(user_question.lower())
        print(f"\nFound {len(context_docs)} relevant documents")
        
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
        
        # Combine context
        context = (
            f"INGREDIENTS:\n{'; '.join(ingredients)}\n\n"
            f"BENEFITS:\n{'; '.join(benefits)}\n\n"
        )
        
        # Format chat history for context
        chat_history = chat_session.get("chat_history", [])
        formatted_history = "\n".join([
            f"Question: {exchange['question']}\nAnswer: {exchange['response']}"
            for exchange in chat_history[-3:]  # Only use last 3 exchanges for context
        ])
        
        # Generate response using the model
        response = model.invoke(
            prompt.format(
                context=context,
                question=user_question,
                chat_history=formatted_history
            )
        )
        
        print("\n✅ Response generated successfully")
        return response
        
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        error_msg = "I apologize, but I'm having trouble analyzing this product right now. Please try asking your question again."
        raise Exception(error_msg) from e

def save_chat_history(user_id: str, chat_session: dict):
    """
    Save chat history to S3 for signed-in users
    """
    # TODO: Implement S3 storage
    pass
