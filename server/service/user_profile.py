import os
from dotenv import load_dotenv
import boto3
import json
from typing import Optional, Dict
from datetime import datetime

load_dotenv()

BUCKET_NAME = "product-buddy"

class UserProfileService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )

    def _save_to_s3(self, path: str, data: Dict) -> None:
        """Save data to S3"""
        try:
            self.s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=path,
                Body=json.dumps(data)
            )
        except Exception as e:
            print(f"Error saving to S3: {str(e)}")
            raise

    def _get_from_s3(self, path: str) -> Optional[Dict]:
        """Get data from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=BUCKET_NAME,
                Key=path
            )
            return json.loads(response['Body'].read().decode('utf-8'))
        except self.s3_client.exceptions.NoSuchKey:
            return None
        except Exception as e:
            print(f"Error reading from S3: {str(e)}")
            raise

    def save_user_info(self, user_email: str, skin_type: str, skin_issues: list, 
                      additional_info: str, location: str) -> Dict:
        """Save user profile information"""
        try:
            user_info = {
                "skin_type": skin_type,
                "skin_issues": skin_issues,
                "additional_info": additional_info,
                "location": location,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            self._save_to_s3(f"users/{user_email}/user_info.json", user_info)
            return {"status": "success", "message": "User information saved successfully"}
        except Exception as e:
            print(f"Error saving user info: {str(e)}")
            raise

    def get_user_info(self, user_email: str) -> Optional[Dict]:
        """Get user profile information"""
        try:
            return self._get_from_s3(f"users/{user_email}/user_info.json")
        except Exception as e:
            print(f"Error getting user info: {str(e)}")
            raise 