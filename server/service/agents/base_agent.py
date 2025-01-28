from abc import ABC, abstractmethod
from typing import Dict, Generator, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from ..embeddings import pinecone_vector_store, embeddings

class BaseAgent(ABC):
    """
    Base agent class that all other agents will inherit from.
    Provides common functionality and required interface for all agents.
    """
    
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            max_tokens=None,
            timeout=30,
            max_retries=3,
            streaming=True
        )
        self.embeddings = embeddings
        self.vector_store = pinecone_vector_store
        
    @abstractmethod
    def can_handle(self, question: str, context: Dict) -> bool:
        """
        Determine if this agent can handle the given question
        
        Args:
            question: The user's question
            context: The current conversation context
            
        Returns:
            bool: True if this agent can handle the question
        """
        pass
        
    @abstractmethod
    def get_required_context(self) -> List[str]:
        """
        Get list of context types this agent needs
        
        Returns:
            List[str]: List of context type identifiers
        """
        pass
        
    @abstractmethod
    def process(
        self,
        question: str,
        context: Dict,
        chat_history: List[Dict]
    ) -> Generator[str, None, None]:
        """
        Process the question and generate a response
        
        Args:
            question: The user's question
            context: The current conversation context
            chat_history: The conversation history
            
        Returns:
            Generator[str, None, None]: Stream of response chunks
        """
        pass
        
    def _get_chat_template(self) -> ChatPromptTemplate:
        """
        Get the chat prompt template for this agent
        
        Returns:
            ChatPromptTemplate: The prompt template
        """
        raise NotImplementedError()
        
    def _extract_insights(
        self,
        question: str,
        response: str,
        context: Dict
    ) -> Optional[Dict]:
        """
        Extract insights from the interaction to update context
        
        Args:
            question: The user's question
            response: The agent's response
            context: The current context
            
        Returns:
            Optional[Dict]: New insights to add to context, if any
        """
        return None 