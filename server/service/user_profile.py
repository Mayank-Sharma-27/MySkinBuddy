import os
from dotenv import load_dotenv
import boto3
import json
from typing import Optional, Dict
from datetime import datetime
from .cookie_service import CookieService
from .auth import AuthService

load_dotenv()

BUCKET_NAME = "product-buddy"

class UserProfileService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        self.cookie_service = CookieService()
        self.auth_service = AuthService()

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
            
            # Save to S3
            self._save_to_s3(f"users/{user_email}/user_info.json", user_info)

            # Update cookie with new profile information
            try:
                # Get current cookie ID from user login data
                user_login = self._get_from_s3(f"users/{user_email}/user_login.json")
                if user_login and user_login.get("cookie_id"):
                    cookie_id = user_login["cookie_id"]
                    cookie_data = self.cookie_service.get_cookie_data(cookie_id)
                    
                    if cookie_data:
                        cookie_data.update({
                            "user_profile": {
                                "skin_type": skin_type,
                                "skin_issues": skin_issues,
                                "additional_info": additional_info,
                                "location": location
                            }
                        })
                        self.cookie_service.save_cookie_data(cookie_id, cookie_data)
            except Exception as cookie_error:
                print(f"Error updating cookie with profile: {str(cookie_error)}")
                # Continue even if cookie update fails
            
            return {"status": "success", "message": "User information saved successfully"}
        except Exception as e:
            print(f"Error saving user info: {str(e)}")
            raise

    def get_user_info(self, cookie_id: str) -> Optional[Dict]:
        """Get user profile information"""
        try:
            return self.cookie_service.get_cookie_data(cookie_id).get("user_profile")
        except Exception as e:
            print(f"Error getting user info: {str(e)}")
            return {}