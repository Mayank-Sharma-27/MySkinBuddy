import boto3
from io import BytesIO
import json
import os
from dotenv import load_dotenv
from skin_sort import scrape_ingredient_data, get_s3_client

load_dotenv()

def test_ingredient_upload(ingredient_url):
    try:
        # Create test ingredient data
        test_ingredient = {
            "ingredient_name": "helianthus-annuus-seed-oil",
            "url": "/ingredients/helianthus-annuus-seed-oil"
        }
        
        s3_client = get_s3_client()
        bucket_name = "skinsortdata"
        folder = "ingredients"
        
        # Generate the file name and path
        file_name = f"{test_ingredient['ingredient_name']}/{test_ingredient['url']}.json".replace(
            '\n', '').replace('ingredients', '').replace('/', '')
        s3_path = folder + "/" + file_name
        
        # Scrape the data
        data = scrape_ingredient_data("https://skinsort.com" + ingredient_url)
        
        # Upload to S3
        data_bytes = json.dumps(data).encode('utf-8')
        file_obj = BytesIO(data_bytes)
        s3_client.upload_fileobj(file_obj, bucket_name, s3_path)
        
        print(f"Successfully uploaded to {s3_path}")
        print("Scraped data:", data)
        
    except Exception as e:
        print("Error during upload:", str(e))


    # Test the function
test_ingredient_upload("/ingredients/helianthus-annuus-seed-oil") 