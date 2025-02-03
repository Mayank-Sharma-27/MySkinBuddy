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
from langchain_core.documents import Document
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
import time
from pinecone import Pinecone, ServerlessSpec
import re
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from service.embeddings import pinecone_vector_store
load_dotenv()

api_key = os.getenv("TOGETHER_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("product-buddy-google")

parser = StrOutputParser()
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

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


def normalize_product_name(name):
    name = name.lower().strip()
    return re.sub(r'[^a-z0-9\s]', '', name) 

prompt = ChatPromptTemplate.from_template(template)

def find_product_with_retriever(product_name: str, top_k: int = 5):
    """
    Finds products using semantic search with embeddings.
    Returns the top_k products based on similarity scores.
    """
    try:
        # Generate embedding for the search query
        query_embedding = embeddings.embed_query(product_name)
        
        # Search using the embedded query
        search_results = pinecone_vector_store.similarity_search_with_score(
            product_name,
            k=top_k,
            filter={"type": "product"}
        )
        
        # Format results
        results = []
        for doc, score in search_results:
            product_entry = {
                "product": doc.metadata.get("product"),
                "brand": doc.metadata.get("brand"),
                "product_id": doc.metadata.get("product_id"),
                "image_url": doc.metadata.get("image_url"),
                "source": doc.metadata.get("source")
            }
            results.append(product_entry)
            
        return results
        
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return []
    
##find_product_by_name_and_brand_with_retriever("18 3 active ingredients vitamin c glow max bright mask", "100-pure")

def get_product_suggestions(query: str, max_suggestions: int = 5):
    """
    Get product suggestions for autocomplete
    """
    try:
        if not query or len(query) < 2:
            return []

        # Normalize the query
        normalized_query = normalize_product_name(query.lower())
        
        # Create a search query focused on product names
        search_query = f"Product name suggestion: {normalized_query}"
        
        # Search using the embedded query
        search_results = pinecone_vector_store.similarity_search_with_relevance_scores(
            search_query,
            k=20
        )

        suggestions = []
        seen_products = set()

        for doc, score in search_results:
            product_name = doc.metadata.get("product", "")
            brand_name = doc.metadata.get("brand", "")
            source = doc.metadata.get("source", "")
            product_id = doc.metadata.get("product_id", "")
            
            if not product_name:
                continue

            # Create a unique identifier
            product_key = f"{brand_name}:{product_name}".lower()
            
            # Skip if we've already seen this product
            if product_key in seen_products:
                continue
                
            # Check if query matches start of product name or brand name
            product_matches = product_name.lower().startswith(normalized_query)
            brand_matches = brand_name.lower().startswith(normalized_query)
            
            # Calculate text similarity for ranking
            query_terms = set(normalized_query.split())
            product_terms = set(product_name.lower().split())
            brand_terms = set(brand_name.lower().split())
            
            text_similarity = len(query_terms & (product_terms | brand_terms)) / len(query_terms)
            
            suggestion = {
                "product": product_name,
                "brand": brand_name,
                "product_id": product_id,
                "text_score": text_similarity,
                "vector_score": score,
                "starts_with": product_matches or brand_matches,
                "source": source
            }
            
            suggestions.append(suggestion)
            seen_products.add(product_key)

        # Sort suggestions:
        # 1. Exact prefix matches first
        # 2. Then by combined score (text + vector similarity)
        sorted_suggestions = sorted(
            suggestions,
            key=lambda x: (
                x["starts_with"],
                (x["text_score"] * 0.7 + x["vector_score"] * 0.3)
            ),
            reverse=True
        )

        # Format the response
        results = []
        for sugg in sorted_suggestions[:max_suggestions]:
            image_url = None
            if sugg["source"]:
                image_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{sugg['source'].replace('json', 'jpg')}"
            
            results.append({
                "label": f"{sugg['brand']} - {sugg['product']}",
                "value": {
                    "product": sugg["product"],
                    "brand": sugg["brand"]
                },
                "image_url": image_url,
                "product_id": sugg["product_id"]
            })

        return results

    except Exception as e:
        print(f"Error getting suggestions: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return []

