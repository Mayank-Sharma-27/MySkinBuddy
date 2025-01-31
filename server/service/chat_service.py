import boto3
import os
from typing import List, Dict, Optional
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from service.agents.product_information_agent import ProductInformationAgent

# Initialize S3 client once
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)
bucket_name = "product-buddy"

executor = ThreadPoolExecutor(max_workers=3)

MESSAGES_PER_FILE = 50  # Number of messages to store per file

def save_chat(cookie_id: str, product_id: str, chat_data: dict):
    """Save chat data to S3 using multiple files"""
    try:
        # Save metadata in main file
        main_key = f"chats/{cookie_id}/{product_id}/metadata.json"
        metadata = {
            "product_name": chat_data.get("product_name"),
            "brand_name": chat_data.get("brand_name"),
            "image_url": chat_data.get("image_url"),
            "created_time": chat_data.get("created_time", datetime.utcnow().isoformat()),
            "last_updated_time": datetime.utcnow().isoformat(),
            "preloaded_context": chat_data.get("preloaded_context", {}),
            "total_messages": 0,
            "current_file_index": 0,
            "product_id": product_id    
        }

        # Try to get existing metadata
        try:
            existing_metadata = s3_client.get_object(
                Bucket=bucket_name,
                Key=main_key
            )
            existing_data = json.loads(existing_metadata['Body'].read())
            metadata.update(existing_data)
        except s3_client.exceptions.NoSuchKey:
            # This is a new chat, create directory structure
            s3_client.put_object(
                Bucket=bucket_name,
                Key=f"chats/{cookie_id}/{product_id}/",
                Body=""
            )

        new_messages = chat_data.get("chat_history", [])
        if not new_messages:
            # Always save metadata even if no new messages
            s3_client.put_object(
                Bucket=bucket_name,
                Key=main_key,
                Body=json.dumps(metadata)
            )
            return

        # Get the current file index and position
        current_file_index = metadata["current_file_index"]
        current_file_key = f"chats/{cookie_id}/{product_id}/messages_{current_file_index}.json"

        try:
            current_file = s3_client.get_object(
                Bucket=bucket_name,
                Key=current_file_key
            )
            current_messages = json.loads(current_file['Body'].read())
        except s3_client.exceptions.NoSuchKey:
            current_messages = []

        # If current file will exceed limit, create new file
        if len(current_messages) + len(new_messages) > MESSAGES_PER_FILE:
            remaining_space = MESSAGES_PER_FILE - len(current_messages)
            if remaining_space > 0:
                current_messages.extend(new_messages[:remaining_space])
                new_messages = new_messages[remaining_space:]
            
            # Save current file
            s3_client.put_object(
                Bucket=bucket_name,
                Key=current_file_key,
                Body=json.dumps(current_messages)
            )

            # Create new file(s) for remaining messages
            while new_messages:
                current_file_index += 1
                current_file_key = f"chats/{cookie_id}/{product_id}/messages_{current_file_index}.json"
                current_batch = new_messages[:MESSAGES_PER_FILE]
                new_messages = new_messages[MESSAGES_PER_FILE:]

                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=current_file_key,
                    Body=json.dumps(current_batch)
                )
        else:
            # Add messages to current file
            current_messages.extend(new_messages)
            s3_client.put_object(
                Bucket=bucket_name,
                Key=current_file_key,
                Body=json.dumps(current_messages)
            )

        # Update metadata
        metadata["current_file_index"] = current_file_index
        metadata["total_messages"] = metadata.get("total_messages", 0) + len(chat_data.get("chat_history", []))
        metadata["last_updated_time"] = datetime.utcnow().isoformat()

        s3_client.put_object(
            Bucket=bucket_name,
            Key=main_key,
            Body=json.dumps(metadata)
        )

    except Exception as e:
        print(f"Error saving chat: {str(e)}")
        raise

def get_chat(cookie_id: str, product_id: str, file_index: int = 0) -> dict:
    """
    Get chat data from S3 using file-based pagination
    Args:
        cookie_id: User's cookie ID
        product_id: Product ID
        file_index: File index number (each file contains a batch of messages)
    """
    try:
        # Get metadata first
        metadata_key = f"chats/{cookie_id}/{product_id}/metadata.json"
        try:
            metadata = json.loads(
                s3_client.get_object(
                    Bucket=bucket_name,
                    Key=metadata_key
                )['Body'].read()
            )
        except s3_client.exceptions.NoSuchKey:
            # Return empty chat data for new chats
            return {
                "product_id": product_id,
                "product_name": "",
                "brand_name": "",
                "image_url": "",
                "chat_history": [],
                "preloaded_context": {},
                "pagination": {
                    "current_page": 0,
                    "total_pages": 1,
                    "total_messages": 0,
                    "has_more": False
                }
            }

        # Get messages from specific file
        messages_key = f"chats/{cookie_id}/{product_id}/messages_{file_index}.json"
        try:
            messages = json.loads(
                s3_client.get_object(
                    Bucket=bucket_name,
                    Key=messages_key
                )['Body'].read()
            )
        except s3_client.exceptions.NoSuchKey:
            messages = []

        return {
            "product_id": product_id,
            "product_name": metadata.get("product_name"),
            "brand_name": metadata.get("brand_name"),
            "image_url": metadata.get("image_url"),
            "chat_history": messages,
            "preloaded_context": metadata.get("preloaded_context", {}),
            "pagination": {
                "current_page": file_index,
                "total_pages": metadata.get("current_file_index", 0) + 1,
                "total_messages": metadata.get("total_messages", 0),
                "has_more": file_index < metadata.get("current_file_index", 0)
            }
        }
    except Exception as e:
        print(f"Error getting chat: {str(e)}")
        raise

def get_all_chats_from_s3(cookie_id: str) -> list:
    """Get all chats metadata from S3"""
    try:
        prefix = f"chats/{cookie_id}/"
        print(f"Getting chat for key: {prefix}")
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix
        )
        
        chats = []
        for obj in response.get('Contents', []):
            # Only process metadata.json files
            if not obj['Key'].endswith('metadata.json'):
                continue
                
            chat_data = s3_client.get_object(
                Bucket=bucket_name,
                Key=obj['Key']
            )
            metadata = json.loads(chat_data['Body'].read())
            
            # Skip chats without product name
            if not metadata.get('product_name'):
                continue
                
            chats.append(metadata)
            
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

    run_product_info()

def get_total_message_count(cookie_id: str) -> int:
    """Get total number of messages across all chats for a user"""
    try:
        chats = get_all_chats_from_s3(cookie_id)
        total_messages = 0
        for chat in chats:
            total_messages += len(chat.get("chat_history", []))
        return total_messages
    except Exception as e:
        print(f"Error getting total message count: {str(e)}")
        raise