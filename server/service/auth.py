import os
from dotenv import load_dotenv
import boto3
import json
from uuid import uuid4
from datetime import datetime, timedelta
import bcrypt
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt
from typing import Optional, Dict

load_dotenv()

# Constants
BUCKET_NAME = "product-buddy"
JWT_SECRET = os.getenv("JWT_SECRET")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
JWT_EXPIRATION_HOURS = 24

class AuthService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )

    def _generate_cookie_id(self) -> str:
        """Generate a unique cookie ID"""
        return str(uuid4())

    def _create_jwt_token(self, user_email: str) -> str:
        """Create a JWT token for the user"""
        expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        return jwt.encode(
            {
                'email': user_email,
                'exp': expiration
            },
            JWT_SECRET,
            algorithm='HS256'
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

    def verify_google_token(self, token: str) -> Optional[str]:
        """Verify Google OAuth token and return user email"""
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                GOOGLE_CLIENT_ID
            )
            return idinfo['email']
        except Exception as e:
            print(f"Error verifying Google token: {str(e)}")
            return None

    def register_user(self, email: str, password: str) -> Dict:
        """Register a new user with email and password"""
        try:
            # Check if user already exists
            user_path = f"users/{email}/login/login.json"
            existing_user = self._get_from_s3(user_path)
            
            if existing_user:
                raise ValueError("User already exists")

            # Hash password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            # Save user data
            user_data = {
                "userEmail": email,
                "password": hashed_password.decode('utf-8')
            }
            self._save_to_s3(user_path, user_data)
            
            # Create and save cookie information
            cookie_id = self._generate_cookie_id()
            cookie_data = {
                "userEmail": email,
                "isLoggedIn": True
            }
            self._save_to_s3(f"cookies/{cookie_id}/info.json", cookie_data)
            
            # Generate JWT token
            token = self._create_jwt_token(email)
            
            return {
                "status": "success",
                "cookie_id": cookie_id,
                "token": token
            }
            
        except Exception as e:
            print(f"Error registering user: {str(e)}")
            raise

    def login_user(self, email: str, password: str) -> Dict:
        """Login user with email and password"""
        try:
            # Get user data
            user_path = f"users/{email}/login/login.json"
            user_data = self._get_from_s3(user_path)
            
            if not user_data:
                raise ValueError("User not found")
            
            # Verify password
            if not bcrypt.checkpw(
                password.encode('utf-8'),
                user_data["password"].encode('utf-8')
            ):
                raise ValueError("Invalid password")
            
            # Create and save cookie information
            cookie_id = self._generate_cookie_id()
            cookie_data = {
                "userEmail": email,
                "isLoggedIn": True
            }
            self._save_to_s3(f"cookies/{cookie_id}/info.json", cookie_data)
            
            # Generate JWT token
            token = self._create_jwt_token(email)
            
            return {
                "status": "success",
                "cookie_id": cookie_id,
                "token": token
            }
            
        except Exception as e:
            print(f"Error logging in user: {str(e)}")
            raise

    def google_login(self, google_token: str) -> Dict:
        """Handle Google login"""
        try:
            email = self.verify_google_token(google_token)
            if not email:
                raise ValueError("Invalid Google token")
            
            # Create user entry if it doesn't exist
            user_path = f"users/{email}/login/login.json"
            if not self._get_from_s3(user_path):
                user_data = {
                    "userEmail": email,
                    "loginType": "google"
                }
                self._save_to_s3(user_path, user_data)
            
            # Create and save cookie information
            cookie_id = self._generate_cookie_id()
            cookie_data = {
                "userEmail": email,
                "isLoggedIn": True
            }
            self._save_to_s3(f"cookies/{cookie_id}/info.json", cookie_data)
            
            # Generate JWT token
            token = self._create_jwt_token(email)
            
            return {
                "status": "success",
                "cookie_id": cookie_id,
                "token": token
            }
            
        except Exception as e:
            print(f"Error with Google login: {str(e)}")
            raise

    def verify_cookie(self, cookie_id: str) -> Optional[str]:
        """Verify cookie and return user email if valid"""
        try:
            cookie_data = self._get_from_s3(f"cookies/{cookie_id}/info.json")
            if cookie_data and cookie_data.get("isLoggedIn"):
                return cookie_data["userEmail"]
            return None
        except Exception as e:
            print(f"Error verifying cookie: {str(e)}")
            return None 