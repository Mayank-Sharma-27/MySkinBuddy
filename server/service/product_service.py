import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
import re
from service.embeddings import pinecone_vector_store, index
from typing import Dict
from .model_service import model_service

load_dotenv()
        
search_template = """You are an expert at converting user product descriptions into optimal search queries for a vector database.
The vector database contains skincare products with the following information structure:
- Product name and brand
- Notable ingredients
- Benefits
- Concerns
- Where it's from
- All ingredients
- Pricing information

Convert the user's product description into a search query that will best match products in our database.
Focus on key aspects like product type, notable ingredients, benefits, or specific characteristics mentioned.

User's product description: {description}

Generate a search query that would best find this type of product. Make it detailed but concise.
Only respond with the search query, nothing else.
"""

search_prompt = ChatPromptTemplate.from_template(search_template)

def normalize_product_name(name):
    name = name.lower().strip()
    return re.sub(r'[^a-z0-9\s]', '', name) 

def create_subtitle(metadata):
    """
    Creates a descriptive subtitle from product metadata.
    """
    subtitle_parts = []
    if metadata.get("where_it_from") and metadata.get("where_it_from") != "Unknown":
        subtitle_parts.append(f"A product of {metadata.get('where_it_from')}")
    
    if metadata.get("notable_ingredients") and metadata.get("notable_ingredients") != "Unknown":
        notable_ingredients = metadata.get("notable_ingredients")
        if isinstance(notable_ingredients, list) and notable_ingredients:
            subtitle_parts.append(f"with {', '.join(notable_ingredients[:3])}")
    
    if metadata.get("benefits") and metadata.get("benefits") != "Unknown":
        benefits = metadata.get("benefits")
        if isinstance(benefits, list) and benefits:
            subtitle_parts.append(f"offering {', '.join(benefits[:3])}")
    
    return " ".join(subtitle_parts) if subtitle_parts else None

def format_product_entry(metadata, score=None):
    """
    Formats a product entry from metadata.
    Works with both direct Pinecone metadata and LangChain Document metadata.
    """
    try:
        # Handle both Document objects and raw metadata
        if hasattr(metadata, 'metadata'):
            metadata = metadata.metadata
            
        if not metadata:
            print("No metadata found")
            return None
            
        subtitle = create_subtitle(metadata)
        
        return {
            "product": metadata.get("product"),
            "brand": metadata.get("brand"),
            "product_id": metadata.get("product_id"),
            "image_url": metadata.get("image_url"),
            "ingredients": metadata.get("notable_ingredients"),
            "where_it_from": metadata.get("where_it_from"),
            "pricing_info": metadata.get("pricing_info"),
            "concerns": metadata.get("concerns"),
            "benefits": metadata.get("benefits"),
            "subtitle": subtitle,
            "vector_score": score
        }
    except Exception as e:
        print(f"Error formatting product entry: {str(e)}")
        return None

def find_product_with_llm_query(description: str, offset: int = 0, limit: int = 20):
    """
    Uses LLM to generate an optimized search query from user description,
    then searches products using semantic search with embeddings.
    """
    try:
        # Generate optimized search query using LLM
        chain = search_prompt | model_service.get_llm_model() | StrOutputParser()
        optimized_query = chain.invoke({"description": description})
        
        # Embed the optimized query
        query_embedding = model_service.get_embeddings_model().embed_query(optimized_query)
        
        # Query Pinecone directly
        query_response = index.query(
            vector=query_embedding,
            top_k=offset + limit,
            filter={"type": "product_overview"},
            include_metadata=True
        )
        
        # Format results
        results = []
        for match in query_response.matches:
            product_entry = format_product_entry(match.metadata, match.score)
            if product_entry:
                results.append(product_entry)
            
        return results
        
    except Exception as e:
        print(f"Error in LLM product search: {str(e)}")
        return []

def find_product_with_retriever(product_name: str, offset: int = 0, limit: int = 20):
    """
    Finds products using semantic search with embeddings.
    Returns paginated results based on offset and limit.
    """
    try:
        normalized_query = normalize_product_name(product_name.lower())
        search_query = f"Search this product: {normalized_query}"
        
        # Embed the search query
        query_embedding = model_service.get_embeddings_model().embed_query(search_query)
        
        # Query Pinecone directly
        query_response = index.query(
            vector=query_embedding,
            top_k=offset + limit,
            filter={"type": "product_overview"},
            include_metadata=True
        )
        
        # Format results
        results = []
        for match in query_response.matches:
            product_entry = format_product_entry(match.metadata, match.score)
            if product_entry:
                results.append(product_entry)
            
        return results
        
    except Exception as e:
        print(f"Error in product retrieval: {str(e)}")
        return []

def get_product_suggestions(query: str, offset: int = 0, limit: int = 20):
    """
    Get paginated product suggestions for autocomplete using direct Pinecone querying
    """
    try:
        if not query or len(query) < 2:
            return []

        normalized_query = normalize_product_name(query.lower())
        search_query = f"Product name suggestion: {normalized_query}"
        
        # Get vector embedding for the query
        query_embedding = model_service.get_embeddings_model().embed_query(search_query)
        
        # Query Pinecone directly
        query_response = index.query(
            vector=query_embedding,
            top_k=offset + limit + 20,
            filter={"type": "product_overview"},
            include_metadata=True
        )

        suggestions = []
        seen_products = set()

        # Process all results
        for match in query_response.matches:
            metadata = match.metadata
            if not metadata or not metadata.get("product"):
                continue
                
            product_name = metadata.get("product", "")
            brand_name = metadata.get("brand", "")
            product_id = metadata.get("product_id", "")
            
            if not product_name:
                continue

            product_key = product_id
            if product_key in seen_products:
                continue
                
            product_matches = product_name.lower().startswith(normalized_query)
            brand_matches = brand_name.lower().startswith(normalized_query)
            
            query_terms = set(normalized_query.split())
            product_terms = set(product_name.lower().split())
            brand_terms = set(brand_name.lower().split())
            
            text_similarity = len(query_terms & (product_terms | brand_terms)) / len(query_terms)
            
            product_entry = format_product_entry(metadata, match.score)
            if not product_entry:
                continue
                
            suggestion = {
                **product_entry,
                "text_score": text_similarity,
                "starts_with": product_matches or brand_matches
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
                "subtitle": sugg["subtitle"],
                "ingredients": sugg["ingredients"],
                "pricing_info": sugg["pricing_info"],
                "concerns": sugg["concerns"],
                "benefits": sugg["benefits"],
                "product_id": sugg["product_id"],
                "image_url": sugg["image_url"]
            })

        return results

    except Exception as e:
        print(f"Error getting suggestions: {str(e)}")
        return []

        

