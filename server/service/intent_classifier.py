from typing import Dict, List
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
import json


class IntentClassifier:
    def __init__(self, model_service):
        self.model_service = model_service
        self.model = self.model_service.get_llm_model()
        
        
    def _get_classification_template(self) -> ChatPromptTemplate:
        system = """You are an expert at analyzing user questions and determining their intent.
        
        TASK:
        Analyze the user's question and provide the following classifications:
        
        1. IS_SKINCARE_RELATED: Determine if the question is related to skincare, beauty products, cosmetics, or personal care.
           - Return "YES" if the question is about skincare/beauty products/cosmetics/ingredients/routines
           - Return "NO" if the question is about unrelated topics
           
        2. REQUIRES_REALTIME: Determine if answering the question properly requires real-time information such as:
           - Current trends or new product releases from the last few months
           - Recent studies or scientific findings about ingredients
           - Comparison with very recently launched products
           - Current pricing or availability that might have changed recently
           - Return "YES" only if real-time information is essential
           - Return "NO" if the question can be answered with general knowledge

        FORMAT YOUR RESPONSE AS JSON:
        ```json
        {{
            "is_skincare_related": "YES/NO",
            "requires_realtime": "YES/NO",
            "explanation": "Brief explanation of your reasoning"
        }}
        ```
        """
        
        return ChatPromptTemplate.from_messages([
            ("system", system),
            ("user", "{question}")
        ])
        
    def classify_intent(self, question: str) -> Dict:
        """
        Classify the intent of a user question.
        
        Args:
            question (str): The user's question to classify
            
        """
        template = self._get_classification_template()
        try:
            chain = ({"question": RunnablePassthrough()} | template | self.model | self._parse_classification_result)
            result = chain.invoke(question)
            return result
        except Exception as e:
            return {
                "is_skincare_related": False,
                "requires_realtime": False,
                "explanation": "Error classifying intent"
            }
    def _parse_classification_result(self, result: str) -> Dict:
        
        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', result.content, re.DOTALL)
            if json_match:
                classification = json.loads(json_match.group(1))
            else:
                is_skincare = "YES" if "is_skincare_related" in result.content else "NO"
                requires_realtime = "YES" if "requires_realtime" in result.content else "NO"
                classification = {
                    "is_skincare_related": is_skincare,
                    "requires_realtime": requires_realtime,
                    "explanation": "Extracted from non-JSON response"
                }
            return {
                "is_skincare_related": classification.get("is_skincare_related", "NO") == "YES",
                "requires_realtime": classification.get("requires_realtime", "NO") == "YES",
                "explanation": classification.get("explanation", "")
            }    
                
        except Exception as e:
            return {
                "is_skincare_related": False,
                "requires_realtime": False,
                "explanation": "Error parsing classification result"
            }
        
        