import os
from dotenv import load_dotenv
import boto3
import json
from uuid import uuid4
from datetime import datetime
from google.oauth2 import id_token
from google.auth.transport import requests
from typing import Optional, Dict
from .cookie_service import CookieService

load_dotenv()

# Constants
BUCKET_NAME = "product-buddy"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

if not GOOGLE_CLIENT_ID:
    raise ValueError("GOOGLE_CLIENT_ID environment variable is not set")

class AuthService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        self.cookie_service = CookieService()

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

    def google_login(self, token: str, cookie_id: str) -> dict:
        """
        Handle Google login. Updates existing cookie with user info
        """
        try:
            # Verify Google token
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), 
                GOOGLE_CLIENT_ID
            )
            user_email = idinfo['email']
            
            # Get existing cookie data
            cookie_data = self.cookie_service.get_cookie_data(cookie_id)
            if not cookie_data:
                raise ValueError("Invalid cookie")
            
            # Update cookie with user info
            cookie_data.update({
                "user_email": user_email,
                "is_logged_in": True,
                "last_login": datetime.utcnow().isoformat()
            })
            
            # Save updated cookie data
            self.cookie_service.save_cookie_data(cookie_id, cookie_data)
            
            # Save user login info
            user_data = {
                "email": user_email,
                "last_login": datetime.utcnow().isoformat(),
                "cookie_id": cookie_id,
                "login_type": "google"
            }
            
            # Save to users/{email}/user_login.json
            self._save_to_s3(f"users/{user_email}/user_login.json", user_data)
            
            return {
                "status": "success",
                "user_email": user_email
            }
            
        except ValueError as e:
            print(f"Token verification failed: {str(e)}")
            raise ValueError("Invalid token")
        except Exception as e:
            print(f"Login error: {str(e)}")
            raise

    def verify_cookie(self, cookie_id: str) -> Optional[str]:
        """Verify cookie and return user email if valid"""
        try:
            cookie_data = self.cookie_service.get_cookie_data(cookie_id)
            if cookie_data and cookie_data.get("is_logged_in"):
                return cookie_data.get("user_email")
            return None
        except Exception as e:
            print(f"Error verifying cookie: {str(e)}")
            return None

    def register_user(self, email: str, password: str, cookie_id: str) -> dict:
        """Register a new user with email and password"""
        try:
            # Check if user already exists
            user_data = self._get_from_s3(f"users/{email}/user_login.json")
            if user_data:
                raise ValueError("User already exists")

            # Get existing cookie data
            cookie_data = self.cookie_service.get_cookie_data(cookie_id)
            if not cookie_data:
                raise ValueError("Invalid cookie")

            # Update cookie with user info
            cookie_data.update({
                "user_email": email,
                "is_logged_in": True,
                "last_login": datetime.utcnow().isoformat()
            })

            # Save updated cookie data
            self.cookie_service.save_cookie_data(cookie_id, cookie_data)

            # Save user registration info
            user_data = {
                "email": email,
                "password": password,  # In production, this should be hashed
                "registered_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat(),
                "cookie_id": cookie_id,
                "login_type": "email"
            }

            # Save to users/{email}/user_login.json
            self._save_to_s3(f"users/{email}/user_login.json", user_data)

            return {
                "status": "success",
                "user_email": email
            }

        except ValueError as e:
            raise
        except Exception as e:
            print(f"Registration error: {str(e)}")
            raise

    def login_user(self, email: str, password: str, cookie_id: str) -> dict:
        """Login user with email and password"""
        try:
            # Get user data
            user_data = self._get_from_s3(f"users/{email}/user_login.json")
            if not user_data:
                raise ValueError("User not found")

            # Verify password (in production, verify hash)
            if user_data.get("password") != password:
                raise ValueError("Invalid password")

            # Get existing cookie data
            cookie_data = self.cookie_service.get_cookie_data(cookie_id)
            if not cookie_data:
                raise ValueError("Invalid cookie")

            # Update cookie with user info
            cookie_data.update({
                "user_email": email,
                "is_logged_in": True,
                "last_login": datetime.utcnow().isoformat()
            })

            # Save updated cookie data
            self.cookie_service.save_cookie_data(cookie_id, cookie_data)

            # Update user login info
            user_data["last_login"] = datetime.utcnow().isoformat()
            user_data["cookie_id"] = cookie_id
            self._save_to_s3(f"users/{email}/user_login.json", user_data)

            return {
                "status": "success",
                "user_email": email
            }

        except ValueError as e:
            raise
        except Exception as e:
            print(f"Login error: {str(e)}")
            raise 