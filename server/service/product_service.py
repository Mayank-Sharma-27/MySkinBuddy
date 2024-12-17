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
from langchain_pinecone.vectorstores import PineconeVectorStore
from langchain_core.documents import Document
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
import time
from pinecone import Pinecone, ServerlessSpec
import re
load_dotenv()

api_key = os.getenv("TOGETHER_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = ChatTogether(api_key =api_key,
                     model= "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("product-buddy")

parser = StrOutputParser()
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

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


def normalize_product_name(name):
    name = name.lower().strip()
    return re.sub(r'[^a-z0-9\s]', '', name) 

prompt = ChatPromptTemplate.from_template(template)

def find_product_by_name_and_brand_with_retriever(product_name: str, brand_name: str = None, top_k: int = 5):
    """
    Finds unique products using semantic search with embeddings.
    If only one exact match is found, includes similar products as suggestions.
    """
    print(f"Searching for - Product: '{product_name}', Brand: '{brand_name}'")
    
    try:
        # Normalize the search terms
        normalized_product_name = normalize_product_name(product_name.lower()) if product_name else ""
        normalized_brand_name = normalize_product_name(brand_name.lower()) if brand_name else ""
        
        # Create a combined search query for embedding
        search_query = f"Product: {normalized_product_name}"
        if normalized_brand_name:
            search_query += f" Brand: {normalized_brand_name}"
        
        print(f"Generating embedding for query: {search_query}")
        
        try:
            # Get vector embeddings for the search query
            query_embedding = embeddings.embed_query(search_query)
            print(f"Embedding generated. Shape/Length: {len(query_embedding)}")
        except Exception as embed_error:
            print(f"Error generating embedding: {str(embed_error)}")
            raise

        try:
            # Search using the embedded query
            print("Performing vector similarity search...")
            search_results = pinecone_vector_store.similarity_search_by_vector_with_score(
                query_embedding, 
                k=10,
                filter={"type": "product"}
            )
            print(f"Found {len(search_results)} initial results")
        except Exception as search_error:
            print(f"Error during vector search: {str(search_error)}")
            print(f"Error type: {type(search_error)}")
            print(f"Error details: {search_error.__dict__}")
            raise

        # Track exact matches and similar products separately
        exact_matches = {}
        similar_products = {}
        
        for doc, score in search_results:
            try:
                product = doc.metadata.get("product", "").lower()
                brand = doc.metadata.get("brand", "").lower()
                source = doc.metadata.get("source", "")
                print(product, brand, source)
                if not product:
                    continue
                
                # Calculate text matching scores
                product_terms = set(normalized_product_name.split())
                doc_product_terms = set(product.split())
                product_score = len(product_terms & doc_product_terms) / len(product_terms)
                
                # Brand matching with normalized names
                brand_score = 0
                if normalized_brand_name:
                    if normalized_brand_name == brand:
                        brand_score = 1.0
                    elif normalized_brand_name in brand or brand in normalized_brand_name:
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
                if brand_score == 1.0 and product_score > 0.8:
                    if product not in exact_matches or final_score > exact_matches[product]["score"]:
                        exact_matches[product] = product_entry
                elif final_score > 0.3:
                    if product not in similar_products or final_score > similar_products[product]["score"]:
                        similar_products[product] = product_entry
                        
            except Exception as doc_error:
                print(f"Error processing document: {str(doc_error)}")
                continue
        
        # Combine and sort results
        results = []
        exact_matches_list = sorted(exact_matches.values(), key=lambda x: x["score"], reverse=True)
        similar_products_list = sorted(similar_products.values(), key=lambda x: x["score"], reverse=True)
        
        results.extend(exact_matches_list)
        
        if len(results) == 1:
            for product in similar_products_list:
                if len(results) >= 3:
                    break
                if product["product"] != results[0]["product"]:
                    results.append(product)
        else:
            for product in similar_products_list:
                if len(results) >= top_k:
                    break
                if product["product"] not in [r["product"] for r in results]:
                    results.append(product)
        
        # Remove score from final output
        for result in results:
            del result["score"]
            
        print(f"Final results: {len(results)} products ({len(exact_matches)} exact matches, {len(similar_products)} similar)")
        return results
        
    except Exception as e:
        print(f"Error during search: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
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
        
        # Get vector embeddings for the query
        query_embedding = embeddings.embed_query(search_query)
        
        # Search using the embedded query
        search_results = pinecone_vector_store.similarity_search_by_vector_with_score(
            embedding=query_embedding,
            k=20,  # Get more results for better filtering
            filter={"type": "product"}
        )

        suggestions = []
        seen_products = set()

        for doc, score in search_results:
            product_name = doc.metadata.get("product", "")
            brand_name = doc.metadata.get("brand", "")
            source = doc.metadata.get("source", "")
            
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
                "image_url": image_url
            })

        return results

    except Exception as e:
        print(f"Error getting suggestions: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return []

