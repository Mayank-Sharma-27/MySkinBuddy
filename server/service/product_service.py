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


load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY  = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "skinsortdata"
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

def find_product_by_name_and_brand_with_retriever(product_name, brand_name=None, top_k=10):
    """
    Finds the top-k product matches from the embedded database using a retriever,
    based on product name and optional brand.

    Parameters:
        product_name (str): The product name provided by the user.
        brand_name (str): The brand name provided by the user (optional).
        top_k (int): Number of top matching products to return. Defaults to 10.

    Returns:
        List[Dict]: A list of top-k matching products with their metadata.
    """
    print(f"User Input - Product: {product_name}, Brand: {brand_name}")
    
    # Initialize retriever with specific search parameters
    pinecone_vector_store = PineconeVectorStore(index=index, embedding=embeddings)
    retriever = pinecone_vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k}
    )

    # Retrieve relevant documents
    retrieved_docs = retriever.get_relevant_documents(product_name)
    
    # Filter results for 'product' type and optional brand match
    product_chunks = [
        doc for doc in retrieved_docs
        if doc.metadata.get("type") == "product" and 
            (brand_name is None or doc.metadata.get("brand", "").lower() == brand_name.lower())
    ]
    
    if not product_chunks:
        print("No matching products found.")
        return []
    
    product_options = [
        {
            "product": doc.metadata["product"],
            "brand": doc.metadata.get("brand", "Unknown Brand"),
            "score": doc.metadata.get("score", "N/A")  # Retrievers may not provide a score
        }
        for doc in product_chunks
    ]
    
    # Print the top matching products
    print("\nTop Matching Products:")
    for idx, product in enumerate(product_options, start=1):
        print(f"{idx}. {product['product']} (Brand: {product['brand']})")
    
    return product_options
    
find_product_by_name_and_brand_with_retriever("18 3 active ingredients vitamin c glow max bright mask", "100-pure")

