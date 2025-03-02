from service.s3_client import get_s3_client
from typing import Dict
from google.cloud import vision
import os
import json
import boto3
import tempfile

class ImagesService:
    def __init__(self):
        self.s3_client = get_s3_client()
        self._setup_google_credentials()

    def _setup_google_credentials(self):
        """Fetch Google credentials from AWS SSM Parameter Store and set them up"""
        try:
            # Check if credentials are provided as environment variable
            if os.getenv('GOOGLE_VISION_CREDENTIALS'):
                try:
                    # Try to parse as JSON string
                    credentials_json = json.loads(os.getenv('GOOGLE_VISION_CREDENTIALS'))
                except json.JSONDecodeError:
                    # If not a valid JSON string, treat as a file path
                    credentials_path = os.getenv('GOOGLE_VISION_CREDENTIALS')
                    with open(credentials_path, 'r') as f:
                        credentials_json = json.load(f)
            else:
                # For local development, load from the local file
                local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                         'google_credentials.json')
                if os.path.exists(local_path):
                    with open(local_path, 'r') as f:
                        credentials_json = json.load(f)
                    print(f"Using local credentials from: {local_path}")
                else:
                    raise FileNotFoundError(f"Google credentials file not found at: {local_path}")
                
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                json.dump(credentials_json, temp_file)
                self.credentials_path = temp_file.name
        except Exception as e:
            print(f"Error fetching Google credentials: {str(e)}")
            raise

    def __del__(self):
        """Cleanup temporary credentials file"""
        try:
            if hasattr(self, 'credentials_path') and os.path.exists(self.credentials_path):
                os.unlink(self.credentials_path)
        except Exception:
            pass

    def get_image_urls(self, image_imformation: Dict):
        file_name = image_imformation["file_name"]
        file_type = image_imformation["file_type"]
        
        # Generate presigned URL with proper parameters
        signed_url = self.s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': 'product-buddy',
                'Key': self.get_file_path(file_name),
                'Expires': 3600,
                'ContentType': file_type
            },
            ExpiresIn=3600,
            HttpMethod='PUT'
        )
        
        return {
            "signed_url": signed_url,
            "file_name": file_name,
            "file_type": file_type
        }
        
    def find_product_with_image(self, image_information: Dict):
        """
        Extracts text from an image stored in S3 using Google Cloud Vision API.
        Returns the extracted text that can be used for product search.
        """
        try:
            bucket_name = 'product-buddy'
            file_path = self.get_file_path(image_information["file_name"])
            
            # Get the image content from S3
            s3_response = self.s3_client.get_object(
                Bucket=bucket_name,
                Key=file_path
            )
            image_content = s3_response['Body'].read()
            
            # Initialize Vision client with credentials
            client = vision.ImageAnnotatorClient.from_service_account_json(self.credentials_path)
            image = vision.Image(content=image_content)
            
            # Perform text detection
            response = client.document_text_detection(image=image)
            
            if not response.text_annotations:
                return {"extracted_text": ""}
                
            extracted_words = []
            seen_words = set()
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            word_text = ''.join([symbol.text for symbol in word.symbols])
                            
                            y_corrds = [vertex.y for vertex in word.bounding_box.vertices]
                            height = max(y_corrds) - min(y_corrds)
                            
                            if word_text.lower() not in seen_words:
                                seen_words.add(word_text.lower())
                                extracted_words.append((word_text, height))
                        
            extracted_words.sort(key=lambda x: x[1], reverse=True)
            
            unique_sizes = {height for _, height in extracted_words}
            if len(unique_sizes) == 1:
                biggest_texts = extracted_words
            else:
                top_percent = int(len(extracted_words) * 0.5)
                biggest_texts = extracted_words[:top_percent]    
            
            
            cleaned_text = ' '.join(word[0] for word in biggest_texts)
            
            return {
                "extracted_text": cleaned_text
            }
            
        except Exception as e:
            print(f"Error in image text extraction: {str(e)}")
            return {"extracted_text": "", "error": str(e)}
        
    def get_file_path(self, file_name: str):
        return f'image-searches/{file_name}'       
        

