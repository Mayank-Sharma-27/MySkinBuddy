import os
from dotenv import load_dotenv
from langchain_together import ChatTogether
from langchain_openai import OpenAIEmbeddings
from langchain_community.chat_models import ChatPerplexity
load_dotenv()

class ModelService:
    _instance = None
    _llm_model = None
    _embeddings_model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelService, cls).__new__(cls)
        return cls._instance

    def get_llm_model(self):
        """
        Returns an instance of the LLM model.
        Args:
            model_name (str): Name of the model to use
        """
        self._llm_model = ChatTogether(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                top_p=0.85,
                temperature=0.2,
                max_tokens=None,
                timeout=30,
                max_retries=3,
                streaming=True
        )
        return self._llm_model

    def get_embeddings_model(self, model_name="text-embedding-3-small"):
        """
        Returns an instance of the embeddings model.
        Args:
            model_name (str): Name of the embeddings model to use
        """
        if self._embeddings_model is None or self._embeddings_model.model != model_name:
            self._embeddings_model = OpenAIEmbeddings(model=model_name)
        return self._embeddings_model
    
    def get_perplexity_model(self):
        """
        Returns an instance of the perplexity model.
        """
        self._perplexity_model = ChatPerplexity(
                                                model="sonar-reasoning",
                                                api_key=os.getenv("PERPLEXITY_API_KEY"),
                                                temperature=0.2,
                                                max_tokens=None,
                                                timeout=30,
                                                max_retries=3,
                                                streaming=True
                                                )
        return self._perplexity_model

# Create a singleton instance
model_service = ModelService()

# Export the model instances
llm = model_service.get_llm_model()
embeddings = model_service.get_embeddings_model() 