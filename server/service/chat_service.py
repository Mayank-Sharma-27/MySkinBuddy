import boto3
import os
from typing import List, Dict, Optional
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from service.agents.product_information_agent import ProductInformationAgent
from service.agents.ingredients_analyzer_agent import IngredientAnalyzerAgent
from service.agents.products_recommendation_agent import ProductRecommendationsAgent

# Initialize S3 client once
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)
bucket_name = "product-buddy"

executor = ThreadPoolExecutor(max_workers=3)

def save_chat(cookie_id: str, product_id: str, chat_data: dict):
    """Save chat data to S3"""
    try:
        # Structure: chats/{cookie_id}/{product_id}.json
        key = f"chats/{cookie_id}/{product_id}.json"
        
        # Try to get existing chat data
        try:
            existing_data = s3_client.get_object(
                Bucket=bucket_name,
                Key=key
            )
            existing_chat = json.loads(existing_data['Body'].read())
            # Append new messages to existing chat history
            existing_chat["chat_history"].extend(chat_data.get("chat_history", []))
            existing_chat["last_updated_time"] = datetime.utcnow().isoformat()
            chat_data = existing_chat
        except:
            # If no existing chat, use new chat data
            chat_data["created_time"] = datetime.utcnow().isoformat()
            chat_data["last_updated_time"] = datetime.utcnow().isoformat()
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(chat_data)
        )
    except Exception as e:
        print(f"Error saving chat: {str(e)}")
        raise

def get_chat(cookie_id: str, product_id: str) -> dict:
    """Get chat data from S3"""
    try:
        key = f"chats/{cookie_id}/{product_id}.json"
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=key
        )
        return json.loads(response['Body'].read())
    except Exception as e:
        print(f"Error getting chat when starting new chat: {str(e)}")
        raise

def get_all_chats_from_s3(cookie_id: str) -> list:
    """Get all chats for a product from S3"""
    try:
        prefix = f"chats/{cookie_id}/"
        print(f"Getting chat for key: {prefix}")
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix
        )
        
        chats = []
        for obj in response.get('Contents', []):
            chat_data = s3_client.get_object(
                Bucket=bucket_name,
                Key=obj['Key']
            )
            chats.append(json.loads(chat_data['Body'].read()))
            
        return sorted(chats, key=lambda x: x['created_time'], reverse=True)
    except Exception as e:
        print(f"Error getting product chats: {str(e)}")
        raise 

def initialize_agents_data(product_data: dict):
    """Initialize data from all agents in background"""
    
    def run_product_info():
        try:
            agent = ProductInformationAgent()
            agent.get_product_info(product_data)
        except Exception as e:
            print(f"Error in product info agent: {str(e)}")

    def run_ingredients_analysis():
        try:
            agent = IngredientAnalyzerAgent()
            agent.analyze_ingredients(product_data)
        except Exception as e:
            print(f"Error in ingredients agent: {str(e)}")

    def run_recommendations():
        try:
            agent = ProductRecommendationsAgent()
            #agent.recommend_products(product_id, {})
        except Exception as e:
            print(f"Error in recommendations agent: {str(e)}")
    run_product_info()