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
from s3_client import get_s3_client 
import re
load_dotenv()
from langchain_openai import OpenAIEmbeddings

api_key = os.getenv("TOGETHER_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = ChatTogether(api_key =api_key,
                     model= "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("product-buddy")
parser = StrOutputParser()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY  = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "product-buddy"
FOLDER_NAME = "products"
BATCH_SIZE = 100

embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
s3_client = get_s3_client()  
pinecone_vector_store = PineconeVectorStore(index=index, embedding=embeddings)

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
                total_documents += 1
                
                # Skip if document count is less than or equal to 1500
                if total_documents <= 0:
                    continue
                
                key = item["Key"]
                if key.endswith(".json"):
                    processed_documents += 1
                    if processed_documents <= 0:
                        continue
                    
                    print(f"Processing document {processed_documents}: {key}")
                    # Rest of the processing logic...
                    json_object = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
                    document_data = json.loads(json_object["Body"].read().decode("utf-8"))
                    
                    product_name = normalize_product_name(key.split('/')[2].replace('.json', '').replace('-', ' '))
                    brand_name = normalize_product_name(key.split('/')[1].replace('-', ' '))
                    
                    ingredients_data = document_data.get('ingredients_overview', [])
                    
                    # Create product embeddings
                    max_ingredients_per_chunk = 1000
                    ingredients = [normalize_ingredient_name(ing['ingredient_name']) for ing in ingredients_data]
                    
                    for i in range(0, len(ingredients), max_ingredients_per_chunk):
                        chunk = ingredients[i:i + max_ingredients_per_chunk]
                        chunk_text = ', '.join(chunk)
                        page_content = (
                            f"Product: {product_name}. Brand: {brand_name}. Ingredients : {chunk_text}."
                        )
                        doc = Document(
                            page_content=page_content,
                            metadata={
                                "product": product_name,
                                "brand": brand_name,
                                "type": "product",
                                "source": key
                            }
                        )
                        print(f"Processing product: {product_name}")
                        pinecone_vector_store.add_documents([doc])
                
            continuation_token = response.get("NextContinuationToken")       
            if not continuation_token:
                break
        print(f"Total products processed and uploaded: {processed_documents}")    
            
    except Exception as e:
        print(f"Error processing products: {e} with {processed_documents} documents")

create_product_embeddings()
#create_ingredient_embeddings()
                        