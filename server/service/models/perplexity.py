from langchain_community.chat_models import ChatPerplexity
from langchain_core.prompts import ChatPromptTemplate
import os 

api_key = os.getenv("PERPLEXITY_API_KEY") 

preplexity = ChatPerplexity(temperature=0, pplx_api_key="YOUR_API_KEY", model="llama-3.1-sonar-small-128k-online")

def get_perplexity_response(prompt: ChatPromptTemplate) -> float:
    return preplexity.invoke(prompt)