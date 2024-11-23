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
from langchain.memory import ConversationBufferMemory


load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY  = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "skinsortdata"
FOLDER_NAME = "products"
BATCH_SIZE = 100
        
template = """
You are a skincare expert who uses product information to determine if a product is suitable for certain skin types and would be useful to those people.
Provide clear, accurate answers based on the context, which includes the product name, brand, ingredients, benefits, and concerns.
If you do not know the answer, respond with "I don't know."

Product: {product_name}
Brand: {brand_name}

Context:
{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

api_key = os.getenv("TOGETHER_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = ChatTogether(api_key =api_key,
                     model= "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("skin-buddy")
parser = StrOutputParser()
embeddings = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-32k-retrieval")

memory = ConversationBufferMemory()

        
pinecone_vector_store = PineconeVectorStore(index=index, embedding=embeddings)
def product_chat(product_name, brand_name):
    retriever = pinecone_vector_store.as_retriever()
    
    while True:
        user_question = input("\n Ask a question about the product (or type 'exit' to end chat):")
        
        if user_question.lower() == "exit":
            print("Ending chat session, Goodbye!")
            
        context_docs = retriever.invoke( user_question.lower()) 
        
        ingredients = []
        benefits = []
        concerns = []

        for doc in context_docs:
            metadata = doc.metadata
            chunk_text = doc.page_content
            if metadata.get("type") == "ingredient":
                ingredients.append(chunk_text)
            elif metadata.get("type") == "benefits":
                benefits.append(chunk_text)
            elif metadata.get("type") == "concerns":
                concerns.append(chunk_text)

        context = f"Product: {product_name}\nBrand: {brand_name}\n"
        context += "\nIngredients:\n" + "\n".join(ingredients) if ingredients else "Ingredients: None\n"
        context += "\nBenefits:\n" + ", ".join(benefits) if benefits else "Benefits: None\n"
        context += "\nConcerns:\n" + ", ".join(concerns) if concerns else "Concerns: None\n"

        print("\nRetrieved Context:")
        print(context)
        
        chain = (
            {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
            | prompt
            | model
            | parser
        )
        
        inputs = {
            "context": context,
            "question": user_question,
            "product_name": product_name,
            "brand_name": brand_name
        }
        response = chain.invoke(inputs)

        # Save chat in memory
        memory.save_context({"user_input": user_question}, {"output": response})

        # Display model's response
        print("\nModel Response:")
        print(response)
        
product_chat("18 3 active ingredients vitamin c glow max bright mask", "100-pure")           