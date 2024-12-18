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

def save_chat(cookie_id: str, chat_id: str, chat_data: Dict) -> None:
    """Save chat data to S3"""
    try:
        s3_key = f"chats/{cookie_id}/{chat_id}.json"
        
        # Update last_updated_time
        chat_data['last_updated_time'] = datetime.utcnow().isoformat()
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json.dumps(chat_data)
        )
    except Exception as e:
        print(f"Error saving chat: {str(e)}")
        raise

def get_chat(cookie_id: str, chat_id: str) -> Optional[Dict]:
    """Get chat data from S3"""
    try:
        s3_key = f"chats/{cookie_id}/{chat_id}.json"
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=s3_key
        )
        return json.loads(response['Body'].read().decode('utf-8'))
    except s3_client.exceptions.NoSuchKey:
        return None
    except Exception as e:
        print(f"Error getting chat: {str(e)}")
        raise

def get_recent_chats(cookie_id: str, limit: int = 5) -> List[Dict]:
    """Get recent chats for a cookie_id"""
    try:
        # List all chat files for this cookie_id
        prefix = f"chats/{cookie_id}/"
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix
        )

        if 'Contents' not in response:
            return []

        # Get all chat files and sort by LastModified
        chat_files = [obj for obj in response['Contents'] if obj['Key'].endswith('.json')]
        chat_files.sort(key=lambda x: x['LastModified'], reverse=True)

        recent_chats = []
        for chat_file in chat_files[:limit]:
            try:
                chat_data = s3_client.get_object(
                    Bucket=bucket_name,
                    Key=chat_file['Key']
                )
                chat = json.loads(chat_data['Body'].read().decode('utf-8'))
                chat['chat_id'] = chat_file['Key'].split('/')[-1].replace('.json', '')
                recent_chats.append({
                    'chat_id': chat['chat_id'],
                    'product': chat.get('product'),
                    'brand': chat.get('brand'),
                    'last_message': chat.get('chat_history', [])[-1]['content'] if chat.get('chat_history') else '',
                    'last_updated_time': chat.get('last_updated_time'),
                    'image_url': chat.get('image_url')
                })
            except Exception as e:
                print(f"Error processing chat file {chat_file['Key']}: {str(e)}")
                continue

        return recent_chats

    except Exception as e:
        print(f"Error fetching recent chats: {str(e)}")
        return [] 