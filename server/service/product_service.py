import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from pinecone import Pinecone, ServerlessSpec
import re
from service.embeddings import pinecone_vector_store
load_dotenv()
        
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

def find_product_with_retriever(product_name: str, offset: int = 0, limit: int = 20):
    """
    Finds products using semantic search with embeddings.
    Returns paginated results based on offset and limit.
    """
    try:
        normalized_query = normalize_product_name(product_name.lower())
        search_query = f"Search this product: {normalized_query}"
        # Fetch extra results to ensure we have enough after filtering
        search_results = pinecone_vector_store.similarity_search_with_relevance_scores(
            normalized_query,
            k=offset + limit
        )
        
        # Format results
        results = []
        for doc, score in search_results[offset:offset + limit]:
            # Print the full document metadata to inspect available fields
            print("Document metadata:", doc.metadata)
            
            product_entry = {
                "product": doc.metadata.get("product"),
                "brand": doc.metadata.get("brand"),
                "product_id": doc.metadata.get("product_id"),
                "image_url": doc.metadata.get("image_url"),
                "source": doc.metadata.get("source"),
                "ingredients": doc.metadata.get("ingredients", [])  # Add ingredients field
            }
            print("Product entry:", product_entry)  # Print formatted entry
            results.append(product_entry)
            
        return results
        
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return []
    
##find_product_by_name_and_brand_with_retriever("18 3 active ingredients vitamin c glow max bright mask", "100-pure")

def get_product_suggestions(query: str, offset: int = 0, limit: int = 20):
    """
    Get paginated product suggestions for autocomplete
    """
    try:
        if not query or len(query) < 2:
            return []

        normalized_query = normalize_product_name(query.lower())
        search_query = f"Product name suggestion: {normalized_query}"
        
        # Fetch extra results to ensure we have enough after filtering
        search_results = pinecone_vector_store.similarity_search_with_relevance_scores(
            search_query,
            k=offset + limit + 15  # Extra buffer for filtering
        )

        suggestions = []
        seen_products = set()

        # Process all results
        for doc, score in search_results:
            product_name = doc.metadata.get("product", "")
            brand_name = doc.metadata.get("brand", "")
            source = doc.metadata.get("source", "")
            product_id = doc.metadata.get("product_id", "")
            image_url = doc.metadata.get("image_url", "")
            
            if not product_name:
                continue

            product_key = f"{brand_name}:{product_name}".lower()
            if product_key in seen_products:
                continue
                
            product_matches = product_name.lower().startswith(normalized_query)
            brand_matches = brand_name.lower().startswith(normalized_query)
            
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
                "source": source,
                "image_url": image_url
            }
            
            suggestions.append(suggestion)
            seen_products.add(product_key)

        # Sort suggestions
        sorted_suggestions = sorted(
            suggestions,
            key=lambda x: (
                x["starts_with"],
                (x["text_score"] * 0.7 + x["vector_score"] * 0.3)
            ),
            reverse=True
        )

        # Apply pagination
        paginated_suggestions = sorted_suggestions[offset:offset + limit]

        # Format the response
        results = []
        for sugg in paginated_suggestions:
            results.append({
                "label": f"{sugg['brand']} - {sugg['product']}",
                "value": {
                    "product": sugg["product"],
                    "brand": sugg["brand"]
                },
                "image_url": sugg["image_url"],
                "product_id": sugg["product_id"]
            })

        return results

    except Exception as e:
        print(f"Error getting suggestions: {str(e)}")
        return []

