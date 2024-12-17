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

api_key = os.getenv("TOGETHER_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = ChatTogether(api_key=api_key,
                     model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("skin-buddy")
parser = StrOutputParser()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "product-buddy"
s3_client = get_s3_client()

embeddings = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-32k-retrieval")
pinecone_vector_store = PineconeVectorStore(index=index, embedding=embeddings)

def normalize_ingredient_name(name):
    name = name.lower().strip()
    return re.sub(r'[^a-z0-9\s]', '', name)

def create_test_embeddings(product_key, ingredient_keys):
    """
    Create embeddings for a specific product and its ingredients
    
    Args:
        product_key (str): S3 key for the product JSON
        ingredient_keys (list): List of S3 keys for ingredient JSONs
    """
    try:
        # Process product
        json_object = s3_client.get_object(Bucket=BUCKET_NAME, Key=product_key)
        document_data = json.loads(json_object["Body"].read().decode("utf-8"))
        
        product_name = product_key.split('/')[2].replace('.json', '')
        brand_name = product_key.split('/')[1]
        
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
                    "type": "product"
                }
            )
            print(f"Processing product: {product_name}")
            pinecone_vector_store.add_documents([doc])
        
        # Process specified ingredients
        for ingredient_key in ingredient_keys:
            try:
                create_ingredient_embeddings(ingredient_key)
            except Exception as e:
                print(f"Error processing ingredient {ingredient_key}: {e}")
                
    except Exception as e:
        print(f"Error processing product {product_key}: {e}")

def create_ingredient_embeddings(ingredient_key):
    """
    Create embeddings for a single ingredient using its S3 key
    """
    try:
        json_object = s3_client.get_object(Bucket="product-buddy", Key=ingredient_key)
        ingredient_data = json.loads(json_object["Body"].read().decode("utf-8"))
        
        ingredient_name = ingredient_key.split('/')[-2] if len(ingredient_key.split('/')) > 2 else "Unknown"
        
        uses = ', '.join(ingredient_data.get('use', []))
        explained = ingredient_data.get('Explained', '')
        concerns = ingredient_data.get('Concerns', [])
        concerns_text = '. '.join(concerns) if concerns else ''
        alt_names = ', '.join(ingredient_data.get('AltNames', []))
        
        page_content = (
            f"Ingredient: {ingredient_name}.\n"
            f"Uses: {uses}.\n"
            f"Details: {explained}\n"
            f"Concerns: {concerns_text}\n"
            f"Alternative Names: {alt_names}."
        )
        
        doc = Document(
            page_content=page_content,
            metadata={
                "ingredient_name": ingredient_name,
                "type": "ingredient"
            }
        )
        
        print(f"Processing ingredient: {ingredient_name}")
        pinecone_vector_store.add_documents([doc])
        
    except Exception as e:
        print(f"Error processing ingredient {ingredient_key}: {e}")
        raise e

# Example usage:
if __name__ == "__main__":
    # These would be replaced with your actual product and ingredient keys
    test_product_key = "products/brand-name/product-name.json"
    test_ingredient_keys = [
        "ingredients/ingredient1.json",
        "ingredients/ingredient2.json"
    ]
    
    create_test_embeddings(test_product_key, test_ingredient_keys) 