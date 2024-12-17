
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
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("product-buddy")
embeddings = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-32k-retrieval")
pinecone_vector_store = PineconeVectorStore(index=index, embedding=embeddings)

def normalize_product_name(name):
    """Convert hyphenated names to space-separated names"""
    # Replace hyphens with spaces
    name = name.replace('-', ' ')
    # Remove any double spaces that might have been created
    name = ' '.join(name.split())
    return name

def fix_product_embeddings(dry_run=True):
    try:
        # Query all vectors with type "product"
        response = index.query(
            vector=[0] * 768,  # dummy vector
            top_k=10000,
            include_metadata=True,
            filter={"type": "product"}
        )

        print(f"Found {len(response.matches)} product vectors to process")
        updated_count = 0
        skipped_count = 0

        for match in response.matches:
            metadata = match.metadata
            old_product_name = metadata.get('product', '')
            
            if '-' in old_product_name:
                # Get the vector ID
                vector_id = match.id
                
                # Normalize the product name
                new_product_name = normalize_product_name(old_product_name)
                
                # Update the page content
                old_content = match.metadata.get('page_content', '')
                new_content = old_content.replace(old_product_name, new_product_name)
                
                # Create new metadata
                new_metadata = {
                    **metadata,
                    'product': new_product_name,
                    'page_content': new_content
                }
                
                # Get the original vector
                vector = match.values
                
                if dry_run:
                    print(f"[DRY RUN] Would update product name from '{old_product_name}' to '{new_product_name}'")
                else:
                    # Update the vector with new metadata
                    index.upsert(vectors=[{
                        'id': vector_id,
                        'values': vector,
                        'metadata': new_metadata
                    }])
                    print(f"Updated product name from '{old_product_name}' to '{new_product_name}'")
                updated_count += 1
            else:
                skipped_count += 1
                if dry_run:
                    print(f"[DRY RUN] Would skip '{old_product_name}' (no hyphens)")

        print(f"\nSummary:")
        print(f"Total vectors found: {len(response.matches)}")
        print(f"Would be updated: {updated_count}")
        print(f"Would be skipped: {skipped_count}")
        if dry_run:
            print("\nThis was a dry run. No changes were made.")
            print("To make actual changes, run with dry_run=False")

    except Exception as e:
        print(f"Error fixing product embeddings: {e}")

if __name__ == "__main__":
    # First do a dry run
    print("Performing dry run...\n")
    fix_product_embeddings(dry_run=True)
    
    # Uncomment the following lines to perform actual updates
    # print("\nPerforming actual updates...\n")
    # fix_product_embeddings(dry_run=False) 