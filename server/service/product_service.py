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

load_dotenv()

api_key = os.getenv("TOGETHER_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = ChatTogether(api_key =api_key,
                     model= "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("skin-buddy")

parser = StrOutputParser()
embeddings = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-32k-retrieval")

pinecone_vector_store = PineconeVectorStore(index=index, embedding=embeddings)
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY  = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "product-buddy"
FOLDER_NAME = "products"
BATCH_SIZE = 100
        
template = """
You are a skincare expert who know from the product information
if the product will be valid for certian skin
In the context from the product details answer the question
if you do not know please say I dont know".

Context: {context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

def find_product_by_name_and_brand_with_retriever(product_name: str, brand_name: str = None, top_k: int = 5):
    """
    Finds unique products using fuzzy search with priority on product name match.
    If only one exact match is found, includes similar products as suggestions.
    """
    print(f"Searching for - Product: '{product_name}', Brand: '{brand_name}'")
    
    retriever = pinecone_vector_store.as_retriever(
        search_kwargs={
            "k": 100  # Get more results for better matching
        }
    )
    
    try:
        docs = retriever.get_relevant_documents(product_name.lower())
        
        # Track exact matches and similar products separately
        exact_matches = {}
        similar_products = {}
        
        for doc in docs:
            product = doc.metadata.get("product", "").lower()
            brand = doc.metadata.get("brand", "").lower()
            source = doc.metadata.get("source", "")
            
            if not product:
                continue
            
            # Calculate scores
            product_terms = set(product_name.lower().split())
            doc_product_terms = set(product.split())
            product_score = len(product_terms & doc_product_terms) / len(product_terms)
            
            # Normalize brand names
            normalized_search_brand = brand_name.lower().replace("-", "").replace(" ", "-") if brand_name else None
            normalized_doc_brand = brand.replace("-", "").replace(" ", "-")
            
            # Check for exact brand match
            is_exact_brand_match = normalized_search_brand == normalized_doc_brand if brand_name else False
            
            # Calculate brand similarity
            brand_score = 0
            if brand_name:
                if is_exact_brand_match:
                    brand_score = 1.0
                elif normalized_search_brand in normalized_doc_brand or normalized_doc_brand in normalized_search_brand:
                    brand_score = 0.5
            else:
                brand_score = 1.0
            
            # Combined score
            final_score = (product_score * 0.7) + (brand_score * 0.3)
            
            product_entry = {
                "product": doc.metadata.get("product"),
                "brand": doc.metadata.get("brand"),
                "source": source,
                "score": final_score
            }
            
            if source:
                image_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{source.replace('json', 'jpg')}"
                product_entry["image_url"] = image_url
            
            # Separate exact matches from similar products
            if is_exact_brand_match and product_score > 0.8:  # High product name match with exact brand
                if product not in exact_matches or final_score > exact_matches[product]["score"]:
                    exact_matches[product] = product_entry
            elif final_score > 0.3:  # Similar products
                if product not in similar_products or final_score > similar_products[product]["score"]:
                    similar_products[product] = product_entry
        
        # Combine results ensuring minimum suggestions
        results = []
        exact_matches_list = sorted(exact_matches.values(), key=lambda x: x["score"], reverse=True)
        similar_products_list = sorted(similar_products.values(), key=lambda x: x["score"], reverse=True)
        
        # Add exact matches first
        results.extend(exact_matches_list)
        
        # If we have only one exact match, ensure we add some similar products
        if len(results) == 1:
            # Add similar products that are different from the exact match
            for product in similar_products_list:
                if len(results) >= 3:  # Ensure at least 3 total suggestions
                    break
                if product["product"] != results[0]["product"]:
                    results.append(product)
        else:
            # Add remaining slots with similar products up to top_k
            for product in similar_products_list:
                if len(results) >= top_k:
                    break
                if product["product"] not in [r["product"] for r in results]:
                    results.append(product)
        
        # Remove score from final output
        for result in results:
            del result["score"]
            
        print(f"Found {len(results)} products ({len(exact_matches)} exact matches, {len(similar_products)} similar)")
        return results
        
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return []
    
##find_product_by_name_and_brand_with_retriever("18 3 active ingredients vitamin c glow max bright mask", "100-pure")

