import requests
from bs4 import BeautifulSoup
import json
import boto3
from io import BytesIO
import time
from botocore.exceptions import ClientError
import re
import os
from dotenv import load_dotenv
import cloudscraper


load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Create a single s3 client instance
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def get_s3_client():
    """Get S3 client with credentials"""
    return boto3.client('s3')

def upload_to_s3(s3_client, bucket_name: str, file_path: str, data: dict):
    """Helper function to upload data to S3"""
    try:
        data_bytes = json.dumps(data).encode('utf-8')
        file_obj = BytesIO(data_bytes)
        s3_client.upload_fileobj(file_obj, bucket_name, file_path)
        return True
    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")
        return False

def scrape_and_upload_products(start_index: int = 0):
    """Main function to scrape and upload product data"""
    with open('products.json', 'r') as file:
        products = json.load(file)
        s3_client = get_s3_client()
        bucket_name = "product-buddy"
        
        for number, product in enumerate(products[start_index:], start=start_index):
            try:
                url = product['product']['product_details']['product_url']
                product_url = url.strip('/')
                folder_path = product_url.lstrip('/')
                
                # Make a single request to get the HTML content
                scrapper = cloudscraper.create_scraper()
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "identity",
                    "Connection": "keep-alive",
                }
                base_url = "https://skinsort.com"
                response = scrapper.get(base_url + url, headers=headers)
                html_content = response.content
                
                # Get product data using the HTML content
                product_data = get_product_data(html_content)
                
                # Get pricing data using the same scraper and HTML content
                pricing_response = scrapper.get(base_url + url + "/vendors", headers=headers)
                pricing_data = get_product_pricing(pricing_response.content)
                
                # Get the product name from the URL for the file path
                product_name = folder_path.split('/')[-1]
                
                # Upload product data with new path structure
                upload_to_s3(s3_client, bucket_name, f"products/{folder_path}/{product_name}.json", product_data)
                upload_to_s3(s3_client, bucket_name, f"products/{folder_path}/pricing.json", pricing_data)
                
                # Get and upload image if available
                try:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    image_tag = soup.find('img', {'fetchpriority': 'high'})
                    
                    if image_tag and image_tag.get('src'):
                        image_response = requests.get(image_tag['src'])
                        image_data = BytesIO(image_response.content)
                        s3_client.upload_fileobj(image_data, bucket_name, f"products/{folder_path}/{product_name}.jpg")
                except Exception as e:
                    print(f"Error uploading image: {str(e)}")
                
                print(f"Processed product {number}: {url}")
                
            except Exception as e:
                print(f"Error processing product {url}: {str(e)}")

def get_product_data(html_content: bytes) -> dict:
    """Extract product information from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Initialize the result dictionary
    result = {
        "brand": "",
        "product": "",
        "ingredients_overview": [],
        "benefits": [],
        "concerns": [],
        "notable_ingredients": []
    }

    # Find the ingredients section using the ID
    ingredients_section = soup.find('div', id='ingredients_explained')
    if ingredients_section:
    # Locate the ingredient list container
        ingredient_list = ingredients_section.find('div', id='ingredients-explained-list')
        if ingredient_list:
            for item in ingredient_list.find_all("div", class_='ingredient-table-row'):
            # Get ingredient name from the link
                name_link = item.find('a')
                if not name_link:
                    continue
            
                ingredient_name = name_link.text.strip()
                ingredient_url = name_link.get('href')
            
            # Get ingredient uses/functions
                uses_div = item.find('div', class_='mt-1 font-medium')
                ingredient_uses = uses_div.text.strip() if uses_div else None
            
            # Get ingredient description from the description div
                info_div = item.find('div', class_='ingredient-description')
                if info_div:
                # Extract only the visible content (exclude "Read more" or "Read less" text/buttons)
                    ingredient_info = " ".join([p.text.strip() for p in info_div.find_all('p')])
                else:
                    ingredient_info = None

                if ingredient_name:  # Only append if there's an ingredient name
                    result['ingredients_overview'].append({
                    "ingredient_name": ingredient_name,
                    "ingredient_url": ingredient_url,
                    "ingredient_uses": ingredient_uses,
                    "ingredient_information": ingredient_info
                    })


    # Find the at_a_glance section
    at_a_glance = soup.find('section', id='at_a_glance')
    if at_a_glance:
        # Find all h3 headers first
        subsection_headers = at_a_glance.find_all('h3', class_='text-sm font-semibold text-warm-gray-800')
        
        for header in subsection_headers:
            header_text = ''.join(header.text.split()).lower()
            print(f"Found section: {header_text}")  # Debug print
            
            # Get the parent div of the header
            subsection = header.parent
            if not subsection:
                continue
                
            # Find the content div that follows the header
            content_div = subsection.find('div', class_='text-warm-gray-500 text-xs font-normal flex flex-wrap gap-2 mt-1')
            if not content_div:
                continue
                
            # Process based on section type
            if header_text == 'notableingredients':
                for button in content_div.find_all('button'):
                    span = button.find('span', class_='font-semibold')
                    if span and span.text.strip() != 'Got it!':
                        result['notable_ingredients'].append(span.text.strip())
                        
            elif header_text == 'benefits':
                for button in content_div.find_all('button'):
                    span = button.find('span', class_='font-semibold')
                    count_span = button.find('span', class_='ml-2')
                    if span and span.text.strip() != 'Got it!':
                        benefit_data = {
                            "benefit_name": span.text.strip()
                        }
                        if count_span:
                            try:
                                benefit_data["count"] = int(count_span.text.strip())
                            except ValueError:
                                pass
                        result['benefits'].append(benefit_data)
                        
            elif header_text == 'concerns':
                for button in content_div.find_all('button'):
                    span = button.find('span', class_='font-semibold')
                    count_span = button.find('span', class_='ml-2')
                    if span and span.text.strip() != 'Got it!':
                        concern_data = {
                            "concern_name": span.text.strip()
                        }
                        if count_span:
                            try:
                                concern_data["count"] = int(count_span.text.strip())
                            except ValueError:
                                pass
                        result['concerns'].append(concern_data)

    # Extract brand and product name
    product_header = soup.find('h1', class_='px-4 lg:px-0 break-words text-left leading-none tracking-tight text-warm-gray-800 text-2xl lg:text-5xl font-bold flex flex-col justify-center lg:justify-start')
    if product_header:
        # Extract the brand name
        brand_element = product_header.find('span', class_='pb-1 text-lg xl:text-3xl font-medium text-warm-gray-900/60')
        if brand_element:
            brand_link = brand_element.find('a')
            result["brand"] = brand_link.text.strip() if brand_link else ""

        # Extract the product name by getting the text node between spans
        # Filter out span elements and get only direct text nodes
        text_nodes = [node for node in product_header.children 
                     if isinstance(node, str) and node.strip()]
        
        # The product name should be the first non-empty text node
        result["product"] = text_nodes[0].strip() if text_nodes else ""
                    

    return result

def get_product_pricing(html_content: bytes) -> dict:
    """Extract pricing information from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    pricing_data = {
        "retailers": []
    }
    
    # Find the turbo-frame content
    turbo_frame = soup.find('turbo-frame', id=lambda x: x and x.startswith('vendors_product_'))
    if not turbo_frame:
        return pricing_data
        
    # Find all retailer links
    retailer_links = turbo_frame.find_all('a', class_='group my-1')
    
    for link in retailer_links:
        retailer_info = {}
        
        # Get retailer name and logo URL from image
        img = link.find('img')
        if img:
            retailer_info["retailer"] = img.get('alt', '').replace(' Logo', '')
            retailer_info["logo_url"] = img.get('src', '')
        
        # Get price if available
        price_span = link.find('span', class_='text-sm font-medium mr-2')
        if price_span:
            price_text = price_span.text.strip()
            try:
                retailer_info["price"] = float(price_text.replace('$', '').replace(',', ''))
            except (ValueError, TypeError):
                retailer_info["price"] = None
        
        # Get action text (Buy/Check price/Search on Amazon)
        action_span = link.find('span', class_='bg-emerald-100')
        if action_span:
            retailer_info["action"] = action_span.text.strip()
        
        # Get retailer URL
        retailer_info["url"] = link.get('href')
        
        # Only add if we have retailer information
        if retailer_info.get("retailer"):
            pricing_data["retailers"].append(retailer_info)
    
    return pricing_data

if __name__ == "__main__":
    scrape_and_upload_products()
