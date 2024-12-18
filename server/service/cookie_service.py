import json
import boto3
import os
from typing import Optional, Dict

class CookieService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        self.bucket_name = "product-buddy"

    def get_cookie_data(self, cookie_id: str) -> Optional[Dict]:
        """Get cookie data from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=f"cookies/{cookie_id}/user_info.json"
            )
            return json.loads(response['Body'].read().decode('utf-8'))
        except self.s3_client.exceptions.NoSuchKey:
            return None
        except Exception as e:
            print(f"Error reading cookie data: {str(e)}")
            raise

    def save_cookie_data(self, cookie_id: str, data: Dict) -> None:
        """Save cookie data to S3"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"cookies/{cookie_id}/user_info.json",
                Body=json.dumps(data)
            )
        except Exception as e:
            print(f"Error saving cookie data: {str(e)}")
            raise

    def update_message_count(self, cookie_id: str) -> int:
        """
        Increment message count in cookie data and return new count
        Returns -1 if no cookie data found
        """
        try:
            cookie_data = self.get_cookie_data(cookie_id)
            if not cookie_data:
                return -1

            # Initialize or increment message count
            message_count = cookie_data.get('messageCount', 0) + 1
            cookie_data['messageCount'] = message_count
            
            self.save_cookie_data(cookie_id, cookie_data)
            return message_count
            
        except Exception as e:
            print(f"Error updating message count: {str(e)}")
            return -1 