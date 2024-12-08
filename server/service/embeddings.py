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
from service.s3_client import get_s3_client 

load_dotenv()

api_key = os.getenv("TOGETHER_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = ChatTogether(api_key =api_key,
                     model= "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("skin-buddy")
parser = StrOutputParser()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY  = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "skinsortdata"
FOLDER_NAME = "products"
BATCH_SIZE = 100

embeddings = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-32k-retrieval")
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

def create_product_embeddings():
    documents = []
    total_documents = 0
    continuation_token = None
    try:
        while True:
            if continuation_token:
                print("Fetching next page of objects..")
                response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=FOLDER_NAME, ContinuationToken=continuation_token)
            else:
                response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=FOLDER_NAME)
            
            for item in response.get("Contents", []):
                total_documents += 1
                
                key = item["Key"]
                if key.endswith(".json"):
                    # Get the JSON content
                    json_object = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
                    document_data = json.loads(json_object["Body"].read().decode("utf-8"))
                    
                    # Extract product and brand from the document data
                    product_name = document_data.get('product', '')
                    brand_name = document_data.get('brand', '')
                    
                    # Get ingredient names from ingredients_overview
                    ingredients = [ing['ingredient_name'] for ing in document_data.get('ingredients_overview', [])]
                    
                    # Create the product document
                    page_content = f"Product: {product_name}. Brand: {brand_name}. Ingredients: {', '.join(ingredients)}."
                    doc = Document(
                        page_content=page_content,
                        metadata={
                            "product": product_name,
                            "brand": brand_name,
                            "type": "product"
                        }
                    )
                    
                    print(f"Processing product: {product_name}")
                    pinecone_vector_store.add_documents([doc])
                
            continuation_token = response.get("NextContinuationToken")       
            if not continuation_token:
                break
        print(f"Total products processed and uploaded: {total_documents}")    
            
    except Exception as e:
        print(f"Error processing products: {e}")

def create_ingredient_embeddings():
    total_documents = 0
    continuation_token = None
    bucket_name = "product-buddy"
    folder_name = "ingredients"
    
    try:
        while True:
            if continuation_token:
                print("Fetching next page of objects..")
                response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_name, ContinuationToken=continuation_token)
            else:
                response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
            
            for item in response.get("Contents", []):
                total_documents += 1
                
                key = item["Key"]
                if key.endswith(".json"):
                    # Get the JSON content
                    json_object = s3_client.get_object(Bucket=bucket_name, Key=key)
                    ingredient_data = json.loads(json_object["Body"].read().decode("utf-8"))
                    
                    # Extract ingredient name from the file path
                    file_parts = key.split('/')
                    ingredient_name = file_parts[-2] if len(file_parts) > 2 else "Unknown"
                    
                    # Format the content sections
                    uses = ', '.join(ingredient_data.get('use', []))
                    explained = ingredient_data.get('Explained', '')
                    concerns = ingredient_data.get('Concerns', [])
                    concerns_text = '. '.join(concerns) if concerns else ''
                    alt_names = ', '.join(ingredient_data.get('AltNames', []))
                    
                    # Create the page content with proper formatting
                    page_content = (
                        f"Ingredient: {ingredient_name}.\n"
                        f"Uses: {uses}.\n"
                        f"Details: {explained}\n"
                        f"Concerns: {concerns_text}\n"
                        f"Alternative Names: {alt_names}."
                    )
                    
                    # Create the Document object
                    doc = Document(
                        page_content=page_content,
                        metadata={
                            "ingredient_name": ingredient_name,
                            "type": "ingredient"
                        }
                    )
                    
                    print(f"Processing ingredient: {ingredient_name}")
                    pinecone_vector_store.add_documents([doc])
                
            continuation_token = response.get("NextContinuationToken")       
            if not continuation_token:
                break
        print(f"Total ingredients processed and uploaded: {total_documents}")    
            
    except Exception as e:
        print(f"Error processing ingredients: {e}")

create_product_embeddings()                        
                        