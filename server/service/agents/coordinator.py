from typing import Dict, Generator, List
from .base_agent import BaseAgent
from .product_agent import ProductAgent
from ..model_service import llm
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

class AgentCoordinator:
    """
    Coordinates multiple specialized agents to handle user questions.
    """
    
    def __init__(self):
        self.product_agent = ProductAgent()
        
        # Template for context generation and model selection
        self.context_template = ChatPromptTemplate.from_template("""You are an expert at analyzing skincare questions and extracting relevant product information.

Your task is to:
1. Determine if the question needs real-time/external data
2. Identify the most relevant parts of the product context for the question

Real-time data is needed if the question:
- Requires current pricing or availability information
- Needs comparison with new/alternative products
- Involves seasonal factors or current trends
- Needs latest research or clinical studies
- Requires information about recent formulation changes

Given:
User Question: {question}
Chat History: {chat_history}
Product Context: {product_context}

Return this JSON:
{{
    "needs_realtime_data": boolean,
    "relevant_context": string  // ONLY extracted and organized information from the provided product context, keeping original wording
}}

Only respond with the JSON, nothing else.""")
        
    def _analyze_question(
        self,
        question: str,
        context: Dict,
        chat_history: List[Dict]
    ) -> Dict:
        """
        Analyze the question to determine model choice and generate relevant context
        """
        # Format chat history for the prompt
        formatted_history = [
            f"{msg['role']}: {msg['content']}"
            for msg in chat_history[-5:]  # Only use last 5 messages for context
        ]
        
        # Prepare the analysis prompt
        prompt_input = {
            "question": question,
            "chat_history": "\n".join(formatted_history),
            "product_context": context.get("product_info", "")
        }
        
        # Create and run the chain
        chain = self.context_template | llm
        result = chain.invoke(prompt_input)
        print("Got result")
        print(result.content)
        try:
            return eval(result.content)  # Convert string JSON to dict
        except Exception as e:
            print(f"Error parsing result: {e}")
            # Fallback if JSON parsing fails
            return {
                "needs_realtime_data": False,
                "relevant_context": context.get("product_info", "")
            }
    
    def process_question(
        self,
        question: str,
        context: Dict,
        chat_history: List[Dict]
    ) -> Generator[str, None, None]:
        """
        Process a question using appropriate agents
        """
        # Analyze question and get context 
        agents_to_use = []
        agents_to_use.append(self.product_agent)
        # For now, just use the first capable agent
        agent = agents_to_use[0]
        
        for chunk in agent.process(question, context, chat_history):
            yield chunk 