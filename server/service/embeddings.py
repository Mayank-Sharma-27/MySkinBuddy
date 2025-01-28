from langchain_together import ChatTogether
import os
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_core.output_parsers import StrOutputParser
import boto3
from langchain_together.embeddings import TogetherEmbeddings
import json
from langchain_core.documents import Document
from .s3_client import get_s3_client 
import re
load_dotenv()
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import hashlib
import time

api_key = os.getenv("TOGETHER_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = ChatTogether(api_key =api_key,
                     model= "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("product-buddy-google")
parser = StrOutputParser()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY  = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "product-buddy"
FOLDER_NAME = "products"
BATCH_SIZE = 100

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", metric="cosine")
s3_client = get_s3_client()  
pinecone_vector_store = PineconeVectorStore(index=index, embedding=embeddings)

# Export both for use in other modules
__all__ = ['embeddings', 'pinecone_vector_store']

def split_json_into_chunks(document_data, metadata):
    chunks = []
    product_chunk_text = f"Product: {metadata['product']}. Brand: {metadata['brand']}."
    chunks.append(Document(page_content=product_chunk_text, metadata={**metadata, "type": "product"}))
    
    for ingredient in document_data.get("ingredients_overview", []):
        chunk_text = f"{ingredient['ingredient_name']}: {ingredient['ingredient_uses']} {ingredient['ingredient_information']}"
        chunks.append(Document(page_content=chunk_text, metadata={**metadata, "type": "ingredient", "ingredient_name": ingredient["ingredient_name"]}))
            
    return chunks       

def normalize_ingredient_name(name):
    name = name.lower().strip()
    return re.sub(r'[^a-z0-9\s]', '', name) 

def normalize_product_name(name):
    name = name.lower().strip()
    return re.sub(r'[^a-z0-9\s]', '', name) 
  
def generate_product_id(product_name, brand_name):
    return int(time.time() * 1000)   

def create_product_embeddings():
    documents = []
    total_documents = 0
    continuation_token = None
    processed_documents = 0
    
    try:
        while True:
            if continuation_token:
                print("Fetching next page of objects..")
                response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=FOLDER_NAME, ContinuationToken=continuation_token)
            else:
                response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=FOLDER_NAME)
            
            for item in response.get("Contents", []):
                key = item["Key"]
                # Only process main product JSON files
                if not (key.endswith('.json') and key.split('/')[-2] == key.split('/')[-1].replace('.json', '')):
                    continue
                
                total_documents += 1
                if total_documents <= 0:
                    continue
                
                processed_documents += 1
                if processed_documents <= 0:
                    continue
                
                try:
                    # Get base path for related files
                    base_path = '/'.join(key.split('/')[:-1])
                    
                    # Load main product data
                    main_product = json.loads(s3_client.get_object(Bucket=BUCKET_NAME, Key=key)["Body"].read().decode("utf-8"))
                    
                    # Get product and brand names with fallback
                    if 'product' in main_product and 'brand' in main_product and main_product['product'].strip() and main_product['brand'].strip():
                        product_name = main_product['product']
                        brand_name = main_product['brand']
                    else:
                        print(f"Warning: Using folder names for product/brand in {key}")
                        product_name = normalize_product_name(key.split('/')[-2])
                        brand_name = normalize_product_name(key.split('/')[1])
                    
                    product_id = generate_product_id(product_name, brand_name)
                    image_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{base_path}/{base_path.split('/')[2]}.jpg"
                    
                    pricing_data = {}
                    try:
                        pricing_key = f"{base_path}/pricing.json"
                        pricing_data = json.loads(s3_client.get_object(Bucket=BUCKET_NAME, Key=pricing_key)["Body"].read().decode("utf-8"))
                    except Exception as e:
                        print(f"Error loading pricing data: {e}")
                    
                    similar_products = {}
                    try:
                        similar_key = f"{base_path}/similar_products.json"
                        similar_products = json.loads(s3_client.get_object(Bucket=BUCKET_NAME, Key=similar_key)["Body"].read().decode("utf-8"))
                    except Exception as e:
                        print(f"Error loading similar products: {e}")
                    
                    # Create different types of chunks
                    
                    # 1. Main Product Information
                    main_content = (
                        f"Product: {product_name}. Brand: {brand_name}. "
                        f"Notable Ingredients: {', '.join(main_product.get('notable_ingredients', []))}. "
                        f"Benefits: {', '.join(b['benefit_name'] for b in main_product.get('benefits', []))}. "
                        f"Concerns: {', '.join(c['concern_name'] for c in main_product.get('concerns', []))}."
                    )
                    
                    main_doc = Document(
                        page_content=main_content,
                        metadata={
                            "product": product_name,
                            "brand": brand_name,
                            "type": "product_overview",
                            "source": key,
                            "product_id": product_id,
                            "image_url": image_url
                        }
                    )
                    pinecone_vector_store.add_documents([main_doc])
                    
                    # 2. Ingredients Information (in chunks)
                    max_ingredients_per_chunk = 10
                    ingredients_data = main_product.get('ingredients_overview', [])
                    
                    for i in range(0, len(ingredients_data), max_ingredients_per_chunk):
                        chunk = ingredients_data[i:i + max_ingredients_per_chunk]
                        ingredients_content = ""
                        for ing in chunk:
                            ingredients_content += f"Ingredient: {ing['ingredient_name']}. Uses: {ing['ingredient_uses']}. "
                            if ing.get('ingredient_information'):
                                ingredients_content += f"Details: {ing['ingredient_information']}. "
                        
                        ing_doc = Document(
                            page_content=ingredients_content,
                            metadata={
                                "product": product_name,
                                "brand": brand_name,
                                "type": "ingredients",
                                "source": key,
                                "product_id": product_id,
                            }
                        )
                        pinecone_vector_store.add_documents([ing_doc])
                    
                    # 3. Pricing Information
                    if pricing_data.get('retailers'):
                        pricing_content = f"Product: {product_name} by {brand_name}. Pricing: "
                        for retailer in pricing_data['retailers']:
                            if retailer.get('price'):
                                pricing_content += f"{retailer['retailer']}: ${retailer['price']}, "
                        
                        price_doc = Document(
                            page_content=pricing_content.rstrip(', '),
                            metadata={
                                "product": product_name,
                                "brand": brand_name,
                                "type": "pricing",
                                "source": key,
                                "product_id": product_id,
                            }
                        )
                        pinecone_vector_store.add_documents([price_doc])
                    
                    # 4. Similar Products Information
                    if similar_products.get('dupes') and len(similar_products['dupes']) > 0:
                        for dupe in similar_products['dupes']:
                            dupe_content = (
                                f"Product: {product_name} by {brand_name} has a dupe: {dupe.get('product_name', '')} "
                                f"by {dupe.get('brand', '')}. Match: {dupe.get('match_percentage', '')}. "
                                f"Attribute Match: {dupe.get('attribute_match', '')}. "
                                f"Ingredient Match: {dupe.get('ingredient_match', '')}. "
                            )
                            if dupe.get('explanation'):
                                dupe_content += f"Explanation: {' '.join(dupe['explanation'])}."
                            
                            dupe_doc = Document(
                                page_content=dupe_content,
                                metadata={
                                    "product": product_name,
                                    "brand": brand_name,
                                    "type": "dupe",
                                    "source": key,
                                    "product_id": product_id,
                                    "image_url": image_url,
                                    "dupe_product": dupe.get('product_name', ''),
                                    "dupe_brand": dupe.get('brand', '')
                                }
                            )
                            pinecone_vector_store.add_documents([dupe_doc])
                    
                    print(f"Processed product {processed_documents}: {product_name}")
                    
                except Exception as e:
                    print(f"Error processing individual product {key}: {e}")
                    continue
            
            continuation_token = response.get("NextContinuationToken")
            if not continuation_token:
                break
            
        print(f"Total products processed and uploaded: {processed_documents}")
        
    except Exception as e:
        print(f"Error in main processing loop: {e} with {processed_documents} documents")

#create_product_embeddings()
#create_ingredient_embeddings()
                        