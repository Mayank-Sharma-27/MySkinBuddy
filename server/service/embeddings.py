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
import re
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import time
import cloudscraper


load_dotenv()
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("product-buddy")
google_index = pc.Index("product-buddy-google")
parser = StrOutputParser()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY  = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "product-buddy"
FOLDER_NAME = "products"
BATCH_SIZE = 100

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
google_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", metric="cosine")
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
) 

class VectorStoreManager:
    _instance = None
    _vector_store = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStoreManager, cls).__new__(cls)
            cls._vector_store = PineconeVectorStore(index=index, embedding=embeddings)
        return cls._instance

    @classmethod
    def get_vector_store(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._vector_store

# Initialize the singleton instance
vector_store_manager = VectorStoreManager()
pinecone_vector_store = vector_store_manager.get_vector_store()

# Export for use in other modules
__all__ = ['embeddings', 'pinecone_vector_store', 'vector_store_manager']

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

def is_product_present(product_name, brand_name):
    """
    Check if a product already exists in the vector database.
    Returns True if product exists, False otherwise.
    """
    normalized_query = f"Product: {product_name}. Brand: {brand_name}."
    results = pinecone_vector_store.similarity_search(
        normalized_query,
        k=1,
        filter={"product": product_name, "brand": brand_name}
    )
    return len(results) > 0

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
                if total_documents <= 23093:
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
                    
                    # Check if product already exists
                    if is_product_present(product_name, brand_name):
                        print(f"Skipping {product_name} by {brand_name} - already exists in database")
                        continue
                        
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
                        
                    if pricing_data.get('retailers'):
                        pricing_content = f"Product: {product_name} by {brand_name}. Pricing: "
                        for retailer in pricing_data['retailers']:
                            if retailer.get('price'):
                                pricing_content += f"{retailer['retailer']}: ${retailer['price']}, "    
                    
                    # Create different types of chunks
                    
                    # 1. Main Product Information
                    main_content = (
                        f"Product: {product_name}. Brand: {brand_name}. "
                        f"Notable Ingredients: {', '.join(main_product.get('notable_ingredients', []))}. "
                        f"Benefits: {', '.join(b['benefit_name'] for b in main_product.get('benefits', []))}. "
                        f"Concerns: {', '.join(c['concern_name'] for c in main_product.get('concerns', []))}."
                        f"Pricing Information: {pricing_content}"
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
                    
                    print(f"Processed product {total_documents}: {product_name}")
                    
                except Exception as e:
                    print(f"Error processing individual product {key}: {e}")
                    continue
            
            continuation_token = response.get("NextContinuationToken")
            if not continuation_token:
                break
            
        print(f"Total products processed and uploaded: {total_documents}")
        
    except Exception as e:
        print(f"Error in main processing loop: {e} with {processed_documents} documents")

def rescrape_products():
    """
    Re-scrapes all products in our database to update their information.
    Process:
    1. Get all product IDs from Pinecone
    2. Process each product one by one
    3. Re-scrape and update data
    """
    try:
        total_processed = 0
        target_products = 70000  # Total number of products to process
        
        scraper = cloudscraper.create_scraper()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "identity",
            "Connection": "keep-alive",
        }
        base_url = "https://skinsort.com"

        # Get all vector IDs first
        print("Fetching all vector IDs...")
        pagination_token = None
        batch_size = 100  # Number of IDs to fetch per page
        
        while total_processed < target_products:
            # Get next batch of IDs
            list_response = index.list_paginated(
                limit=batch_size,
                pagination_token=pagination_token,
                namespace=''
            )
             
            # Process this batch of IDs
            for vector in list_response.vectors:
                vector_id = vector.id
                try:
                    if total_processed >= target_products:
                        print("Reached target number of products")
                        break

                    # Fetch single vector
                    fetch_response = index.fetch(ids=[vector_id])
                    if not fetch_response.vectors or vector_id not in fetch_response.vectors:
                        print(f"Could not fetch vector {vector_id}")
                        continue

                    vector = fetch_response.vectors[vector_id]
                    metadata = vector.metadata
                    source = metadata.get('source', '')
                    
                    if not source:
                        print(f"No source found for product {metadata.get('product', 'unknown')}")
                        continue
                        
                    # Skip if where_it_from already exists in metadata
                    if metadata.get('where_it_from'):
                        print(f"Skipping product {metadata.get('product')} - already has where_it_from data")
                        total_processed += 1
                        continue
                    
                    # Remove the .json extension and get the product path
                    product_path = '/'.join(source.split('/')[:-1])
                    if not product_path:
                        continue
                        
                    print(f"Processing product: {product_path}")
                    
                    # Check if the URL ends with /dupes
                    if product_path.endswith('/dupes'):
                        print(f"Deleting dupe document with ID: {vector_id}")
                        index.delete(ids=[vector_id])
                        total_processed += 1
                        continue
                        
                    # Construct the full URL
                    url = f"{base_url}/{product_path}"
                    
                    # Get the product data
                    page_response = scraper.get(url, headers=headers)
                    html_content = page_response.content
                    
                    # Get product data using the HTML content
                    #product_data = get_product_data(html_content)
                    pricing_response = scraper.get(url + "/vendors", headers=headers)
                    #pricing_data = get_product_pricing(pricing_response.content)
                    pricing_data = {}
                    product_data = {}
                    
                    princing_information = ""
                    pricing = []
                    for r in pricing_data.get('retailers', []):
                        if r.get('price') is not None:
                            princing_information += f"{r.get('retailer')}: ${r.get('price')}, "
                            pricing.append({
                                "retailer": r.get('retailer'),
                                "price": r.get('price'),
                                "url": r.get('url')
                            })
                    
                    if not product_data.get('brand') or not product_data.get('product'):
                        print(f"Missing brand or product name for {url}")
                        continue
                    
                    # Update the vector store with new data
                    main_content = (
                        f"Product: {product_data['product']}. Brand: {product_data['brand']}. "
                        f"Notable Ingredients: {', '.join(product_data.get('notable_ingredients', []))}. "
                        f"Benefits: {', '.join(b['benefit_name'] for b in product_data.get('benefits', []))}. "
                        f"Concerns: {', '.join(c['concern_name'] for c in product_data.get('concerns', []))}. "
                        f"Where it's from: {product_data.get('where_it_from')}. "
                        f"All Ingredients: {', '.join(ingredient['ingredient_name'] for ingredient in product_data.get('ingredients_overview', []))}. "
                        f"Pricing Information: {princing_information}"
                    )
                    
                    # Create metadata dictionary
                    metadata = {
                        "product": product_data['product'],
                        "brand": product_data['brand'],
                        "type": "product_overview",
                        "source": source,
                        "product_id": metadata.get('product_id'),
                        "image_url": metadata.get('image_url'),
                        "where_it_from": product_data.get('where_it_from') or "Unknown",
                        "notable_ingredients": product_data.get('notable_ingredients', []) or "Unknown",
                        "benefits": [b['benefit_name'] for b in product_data.get('benefits', [])] or "Unknown",
                        "concerns": [c['concern_name'] for c in product_data.get('concerns', [])] or "Unknown",
                        "pricing_info": princing_information or "Unknown",
                        "ingredients": [ingredient['ingredient_name'] for ingredient in product_data.get('ingredients_overview', [])] or "Unknown"
                    }
                    
                    # Generate vector for the content
                    vector = embeddings.embed_query(main_content)
                    
                    # Update the vector
                    index.upsert(
                        vectors=[{
                            'id': vector_id,
                            'values': vector,
                            'metadata': metadata
                        }]
                    )
                    total_processed += 1
                    print(f"Updated product: {product_data['product']} by {product_data['brand']} total processed: {total_processed}")
                    
                    # Sleep briefly to avoid rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error processing product {source}: {str(e)}")
                    continue

            # Get pagination token for next batch
            pagination_token = list_response.pagination.next
            if not pagination_token:
                print("No more pages to process")
                break
                
            # Sleep briefly between batches
            time.sleep(0.5)

        print(f"Completed processing. Total products processed: {total_processed}")
            
    except Exception as e:
        print(f"Error in main processing loop: {str(e)}")
        print(f"Processed {total_processed} products before error")

#rescrape_products()
#create_ingredient_embeddings()
                        