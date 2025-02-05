import boto3
import os
from typing import List, Dict, Optional
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from service.agents.product_information_agent import ProductInformationAgent

class ChatService:
    def __init__(self):
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        self.bucket_name = "product-buddy"
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.MESSAGES_PER_FILE = 50  # Number of messages to store per file

    def save_chat(self, cookie_id: str, product_id: str, chat_data: dict):
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
                existing_metadata = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=main_key
                )
                existing_data = json.loads(existing_metadata['Body'].read())
                metadata.update(existing_data)
            except self.s3_client.exceptions.NoSuchKey:
                # This is a new chat, create directory structure
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=f"chats/{cookie_id}/{product_id}/",
                    Body=""
                )

            new_messages = chat_data.get("chat_history", [])
            if not new_messages:
                # Always save metadata even if no new messages
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=main_key,
                    Body=json.dumps(metadata)
                )
                return

            # Get the current file index and position
            current_file_index = metadata["current_file_index"]
            current_file_key = f"chats/{cookie_id}/{product_id}/messages_{current_file_index}.json"

            try:
                current_file = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=current_file_key
                )
                current_messages = json.loads(current_file['Body'].read())
            except self.s3_client.exceptions.NoSuchKey:
                current_messages = []

            # If current file will exceed limit, create new file
            if len(current_messages) + len(new_messages) > self.MESSAGES_PER_FILE:
                remaining_space = self.MESSAGES_PER_FILE - len(current_messages)
                if remaining_space > 0:
                    current_messages.extend(new_messages[:remaining_space])
                    new_messages = new_messages[remaining_space:]
                
                # Save current file
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=current_file_key,
                    Body=json.dumps(current_messages)
                )

                # Create new file(s) for remaining messages
                while new_messages:
                    current_file_index += 1
                    current_file_key = f"chats/{cookie_id}/{product_id}/messages_{current_file_index}.json"
                    current_batch = new_messages[:self.MESSAGES_PER_FILE]
                    new_messages = new_messages[self.MESSAGES_PER_FILE:]

                    self.s3_client.put_object(
                        Bucket=self.bucket_name,
                        Key=current_file_key,
                        Body=json.dumps(current_batch)
                    )
            else:
                # Add messages to current file
                current_messages.extend(new_messages)
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=current_file_key,
                    Body=json.dumps(current_messages)
                )

            # Update metadata
            metadata["current_file_index"] = current_file_index
            metadata["total_messages"] = metadata.get("total_messages", 0) + len(chat_data.get("chat_history", []))
            metadata["last_updated_time"] = datetime.utcnow().isoformat()

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=main_key,
                Body=json.dumps(metadata)
            )

        except Exception as e:
            raise

    def get_chat(self, cookie_id: str, product_id: str, file_index: int = 0) -> dict:
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
                    self.s3_client.get_object(
                        Bucket=self.bucket_name,
                        Key=metadata_key
                    )['Body'].read()
                )
            except self.s3_client.exceptions.NoSuchKey:
                # Return empty chat data with welcome message for new chats
                return {
                    "product_id": product_id,
                    "product_name": "",
                    "brand_name": "",
                    "image_url": "",
                    "chat_history": [{
                        "content": "Hi! I am your personalized skincare buddy. How can I help you today?",
                        "role": "assistant",
                        "id": "welcome_message",
                        "timestamp": datetime.utcnow().isoformat()
                    }],
                    "preloaded_context": {},
                    "pagination": {
                        "current_page": 0,
                        "total_pages": 1,
                        "total_messages": 1,
                        "has_more": False
                    }
                }

            # Get messages from specific file
            messages_key = f"chats/{cookie_id}/{product_id}/messages_{file_index}.json"
            try:
                messages = json.loads(
                    self.s3_client.get_object(
                        Bucket=self.bucket_name,
                        Key=messages_key
                    )['Body'].read()
                )
                # Deduplicate messages based on content and timestamp
                seen_messages = set()
                unique_messages = []
                for msg in messages:
                    msg_key = f"{msg['content']}_{msg['timestamp']}"
                    if msg_key not in seen_messages:
                        seen_messages.add(msg_key)
                        unique_messages.append(msg)
                messages = unique_messages
                
            except self.s3_client.exceptions.NoSuchKey:
                # For empty message files, include welcome message if it's the first page
                if file_index == 0:
                    product_name = metadata.get("product_name", "")
                    brand_name = metadata.get("brand_name", "")
                    welcome_msg = f"Hi! I am your personalized skincare buddy. I'm here to help you with {product_name} by {brand_name}. How can I assist you today?"
                    messages = [{
                        "content": welcome_msg,
                        "role": "assistant",
                        "id": "welcome_message",
                        "timestamp": datetime.utcnow().isoformat()
                    }]
                else:
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
            raise

    def get_all_chats_from_s3(self, cookie_id: str) -> list:
        """Get all chats metadata from S3"""
        try:
            prefix = f"chats/{cookie_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )

            chats = []
            # First, collect all metadata files
            metadata_files = [obj['Key'] for obj in response.get('Contents', []) 
                            if obj['Key'].endswith('metadata.json')]
            print(f"Metadata files: {metadata_files}")
            
            # Process each metadata file
            for metadata_key in metadata_files:
                try:
                    chat_data = self.s3_client.get_object(
                        Bucket=self.bucket_name,
                        Key=metadata_key
                    )
                    metadata = json.loads(chat_data['Body'].read())
                    
                    # Skip chats without product name
                    if not metadata.get('product_name'):
                        continue
                    
                    # Add chat to list if it has valid metadata
                    chats.append(metadata)
                        
                except Exception as e:
                    print(f"Error processing metadata file {metadata_key}: {str(e)}")
                    continue
                
            return sorted(chats, key=lambda x: x.get('last_updated_time', x.get('created_time', '')), reverse=True)
        except Exception as e:
            print(f"Error getting all chats: {str(e)}")
            return []

    def initialize_agents_data(self, product_data: dict):
        """Initialize data from all agents in background"""
        
        def run_product_info():
            try:
                agent = ProductInformationAgent()
                agent.get_product_info(product_data)
            except Exception:
                pass

        run_product_info()

    def get_total_message_count(self, cookie_id: str) -> int:
        """Get total number of messages across all chats for a user"""
        try:
            total_messages = 0
            prefix = f"chats/{cookie_id}/"
            
            # List all objects in the user's chat directory
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            # Process each metadata file to get total messages
            for obj in response.get('Contents', []):
                if obj['Key'].endswith('metadata.json'):
                    metadata = json.loads(
                        self.s3_client.get_object(
                            Bucket=self.bucket_name,
                            Key=obj['Key']
                        )['Body'].read()
                    )
                    total_messages += metadata.get('total_messages', 0)
                    
            return total_messages
        except Exception as e:
            print(f"Error getting total message count: {str(e)}")
            return 0

    def get_recent_chat(self, cookie_id: str, product_id: str) -> dict:
        """
        Get chat data from S3 with only the last 2 pages of messages for context
        Args:
            cookie_id: User's cookie ID
            product_id: Product ID
        """
        try:
            # Get metadata first
            metadata_key = f"chats/{cookie_id}/{product_id}/metadata.json"
            try:
                metadata = json.loads(
                    self.s3_client.get_object(
                        Bucket=self.bucket_name,
                        Key=metadata_key
                    )['Body'].read()
                )
            except self.s3_client.exceptions.NoSuchKey:
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

            current_file_index = metadata.get("current_file_index", 0)
            messages = []

            # Get last two file indices
            start_index = max(0, current_file_index - 1)
            file_indices = range(start_index, current_file_index + 1)

            def load_messages(file_index):
                messages_key = f"chats/{cookie_id}/{product_id}/messages_{file_index}.json"
                try:
                    file_messages = json.loads(
                        self.s3_client.get_object(
                            Bucket=self.bucket_name,
                            Key=messages_key
                        )['Body'].read()
                    )
                    return file_messages
                except self.s3_client.exceptions.NoSuchKey:
                    return []

            # Load messages in parallel
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_to_index = {executor.submit(load_messages, idx): idx for idx in file_indices}
                for future in as_completed(future_to_index):
                    messages.extend(future.result())

            # Deduplicate messages based on content and timestamp
            seen_messages = set()
            unique_messages = []
            for msg in messages:
                msg_key = f"{msg['content']}_{msg['timestamp']}"
                if msg_key not in seen_messages:
                    seen_messages.add(msg_key)
                    unique_messages.append(msg)
            messages = unique_messages

            return {
                "product_id": product_id,
                "product_name": metadata.get("product_name"),
                "brand_name": metadata.get("brand_name"),
                "image_url": metadata.get("image_url"),
                "chat_history": messages,
                "preloaded_context": metadata.get("preloaded_context", {}),
                "pagination": {
                    "current_page": current_file_index,
                    "total_pages": current_file_index + 1,
                    "total_messages": metadata.get("total_messages", 0),
                    "has_more": False
                }
            }
        except Exception as e:
            raise