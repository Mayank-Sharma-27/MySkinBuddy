import os
from dotenv import load_dotenv
import json
from service.s3_client import get_s3_client
from duckduckgo_search import DDGS
from service.chat_service import ChatService
from service.s3_client import get_s3_client
from service.embeddings import pinecone_vector_store
from service.user_profile import UserProfileService

duckduckgo = DDGS(timeout=20)
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY  = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "product-buddy"
FOLDER_NAME = "chats"

s3_client = get_s3_client()
chat_service = ChatService()
user_profile_service = UserProfileService()
class ContextBuilder:
    def __init__(self):
        self.chat_service = ChatService()
        
    def get_context(self, cookie_id: str, product_id: str) -> dict:
        """Get or build context for a product chat"""
        try:
            # Get existing context from chat service
            chat_data = self.chat_service.get_chat(cookie_id, product_id)
            if chat_data and chat_data.get("preloaded_context"):
                return chat_data["preloaded_context"]
                
            # Build new context using get_initial_context
            context = get_initial_context(product_id)
            context["user_information"] = user_profile_service.get_user_info(cookie_id)
            
            return context
            
        except Exception as e:
            print(f"Error building context: {str(e)}")
            raise

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
        
        producut_id_int = int(product_id)
        # Get product document from Pinecone
        product_filter = {
            "product_id": producut_id_int,
            "type": "product_overview"
        }
        
        product_docs = pinecone_vector_store.search(
            "",  # Empty query to get exact match
            k=1,
            filter=product_filter,
            search_type="similarity"
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