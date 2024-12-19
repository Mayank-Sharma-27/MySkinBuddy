import boto3
import os
from typing import List, Dict, Optional
import json
from datetime import datetime

# Initialize S3 client once
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)
bucket_name = "product-buddy"

def save_chat(cookie_id: str, product_id: str, chat_id: str, chat_data: dict):
    """Save chat data to S3"""
    try:
        # Structure: chats/{cookie_id}/{product_id}/{chat_id}.json
        key = f"chats/{cookie_id}/{product_id}/{chat_id}.json"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(chat_data)
        )
    except Exception as e:
        print(f"Error saving chat: {str(e)}")
        raise

def get_chat(cookie_id: str, product_id: str, chat_id: str) -> dict:
    """Get chat data from S3"""
    try:
        key = f"chats/{cookie_id}/{product_id}/{chat_id}.json"
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=key
        )
        return json.loads(response['Body'].read())
    except Exception as e:
        print(f"Error getting chat: {str(e)}")
        raise

def get_recent_chats(cookie_id: str) -> list:
    """Get all chats for a product"""
    try:
        prefix = f"chats/{cookie_id}/"
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