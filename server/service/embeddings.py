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
        
    if document_data.get("benefits"):
        benefits_text = ", ".join(benefit["benefit_name"] for benefit in document_data["benefits"])
        chunks.append(Document(page_content=f"Benefits: {benefits_text}", metadata={**metadata, "type": "benefits"}))
        
    if document_data.get("concerns"):
        concerns_text = ", ".join(concern["concern_name"] for concern in document_data["concerns"])
        chunks.append(Document(page_content=f"Concerns: {concerns_text}", metadata={**metadata, "type": "concerns"}))
        
    return chunks       

def create_embeddings():
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
                total_documents +=1
                if total_documents > 2:
                    break
                
                key = item["Key"]
                if key.endswith(".json"):
                    json_object = s3_client.get_object(Bucket=BUCKET_NAME, Key =key)
                    document_data = json.loads(json_object["Body"].read().decode("utf-8"))
                    parts = key.split('/')
                    
                if len(parts) >= 3:
                    brand = parts[1]
                    product = parts[2].replace('.json', '').replace('-', ' ')    
                 
                metadata = {"source": key, "brand" : brand, "product": product}
                
                chunks = split_json_into_chunks(document_data, metadata)  
                print(f"Chunks to be uploaded {len(chunks)}")
                for chunk in chunks:
                    pinecone_vector_store.add_documents([chunk])
                
            continuation_token = response.get("NextContinuationToken")       
            if not continuation_token:
                break
        print(f"Total documents processed and uploaded: {total_documents}")    
            
    except Exception as e:
        print(f"Error fetching documents: {e}")         
                        
create_embeddings()                        
                        