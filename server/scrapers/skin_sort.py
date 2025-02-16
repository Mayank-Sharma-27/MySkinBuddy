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
import xml.etree.ElementTree as ET


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
    
def get_similar_products(html_content: bytes) -> dict:
    """Extract similar products information from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    similar_products = {
        "dupes": []
    }
    
    # Find all dupe containers
    dupe_containers = soup.find_all('div', class_=lambda x: x and 'border-2 border-blue-gray-500' in x)
    
    for container in dupe_containers:
        dupe_info = {}
        product_links = container.find_all('a', class_='flex flex-col h-full items-center justify-center w-1/2 group')
        if len(product_links) >= 2:
            # Dupe product (first link)
            dupe_product = product_links[0]
            dupe_info['dupe_product'] = {
                'url': dupe_product.get('href'),
                'image_url': dupe_product.find('img').get('src') if dupe_product.find('img') else None
            }
            
            # Original product (second link)
            original_product = product_links[1]
            dupe_info['original_product'] = {
                'url': original_product.get('href'),
                'image_url': original_product.find('img').get('src') if original_product.find('img') else None
            }
        
        # Get product name and brand
        product_title = container.find('h2', class_='font-header')
        if product_title:
            brand = product_title.find('span', class_='font-light')
            dupe_info['brand'] = brand.text.strip() if brand else ''
            # Get product name by removing brand name from full title
            full_title = product_title.text.strip()
            dupe_info['product_name'] = full_title.replace(dupe_info['brand'], '').strip()
        
        # Get match percentage
        match_info = container.find('div', class_='bg-yellow-100')
        if match_info:
            match_percentage = match_info.find('span', class_='text-4xl')
            if match_percentage:
                dupe_info['match_percentage'] = match_percentage.text.strip()
            
            # Get attribute and ingredient match
            match_details = match_info.find_all('div', class_='bg-white')
            for detail in match_details:
                if 'Attribute Match' in detail.text:
                    dupe_info['attribute_match'] = detail.text.split('Attribute Match')[0].strip()
                elif 'Ingredient Match' in detail.text:
                    dupe_info['ingredient_match'] = detail.text.split('Ingredient Match')[0].strip()
        
        # Get dupe explanation
        dupe_explained = container.find_all('h3', class_='text-blue-gray-800')
        dupe_explained = [h3 for h3 in dupe_explained if 'Dupe Explained' in h3.text]
        if dupe_explained:
            explanation_div = dupe_explained[0].find_next('div', class_='prose')
            if explanation_div:
                explanations = []
                for p in explanation_div.find_all('p'):
                    explanations.append(p.text.strip())
                dupe_info['explanation'] = explanations
        
        # Get price comparison
        price_comparison = container.find_all('h3', class_='text-blue-gray-800')
        price_comparison = [h3 for h3 in price_comparison if 'Price Comparison' in h3.text]
        if price_comparison:
            price_div = price_comparison[0].find_next('div', class_='grid')
            if price_div:
                prices = {}
                price_buttons = price_div.find_all('button')
                for button in price_buttons:
                    product_name = button.find('img').get('alt') if button.find('img') else None
                    price_text = button.find('div', class_='font-header text-left').text.strip() if button.find('div', class_='font-header text-left') else None
                    if product_name and price_text:
                        prices[product_name] = price_text
                dupe_info['price_comparison'] = prices
        
        similar_products['dupes'].append(dupe_info)
    
    return similar_products

def count_existing_products(s3_client, bucket_name: str) -> int:
    """Count number of unique products already uploaded to S3"""
    try:
        # List all objects in the bucket
        paginator = s3_client.get_paginator('list_objects_v2')
        product_count = 0
        
        # Paginate through all objects
        for page in paginator.paginate(Bucket=bucket_name):
            if 'Contents' in page:
                for obj in page['Contents']:
                    file_path = obj['Key']
                    path_parts = file_path.split('/')
                    
                    # Check if it's a json file and if the filename matches its parent folder
                    if len(path_parts) >= 2 and path_parts[-1].endswith('.json'):
                        folder_name = path_parts[-2]
                        file_name = path_parts[-1].replace('.json', '')
                        if folder_name == file_name:
                            product_count += 1
        
        return product_count
    except Exception as e:
        print(f"Error counting products: {str(e)}")
        return 0

def check_missing_data():
    """Check for products with missing brand/product and rescrape them"""
    s3_client = get_s3_client()
    bucket_name = "product-buddy"
    scraper = cloudscraper.create_scraper()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",
        "Connection": "keep-alive",
    }

    found_missing_data = False

    # List all objects in the bucket/product path
    paginator = s3_client.get_paginator('list_objects_v2')
    
    for page in paginator.paginate(Bucket=bucket_name, Prefix='product/'):
        if 'Contents' not in page:
            continue

        for obj in page['Contents']:
            file_path = obj['Key']
            
            # Only process main product .json files (not pricing or similar_products)
            path_parts = file_path.split('/')
            if len(path_parts) < 3 or not file_path.endswith('.json') or 'pricing' in file_path or 'similar_products' in file_path:
                continue
                
            # Check if the filename matches its parent folder (main product file)
            folder_name = path_parts[-2]
            file_name = path_parts[-1].replace('.json', '')
            if folder_name != file_name:
                continue

            # Get the current product data
            try:
                response = s3_client.get_object(Bucket=bucket_name, Key=file_path)
                product_data = json.loads(response['Body'].read().decode('utf-8'))
                
                # Only proceed if brand or product is empty
                if not product_data.get('brand') or not product_data.get('product'):
                    found_missing_data = True
                    print(f"Found missing data in: {file_path}")
                    
                    # Extract the product URL from the file path
                    url_path = '/'.join(file_path.split('/')[:-1])  # Remove the filename
                    product_url = f"https://skinsort.com/{url_path}"
                    
                    # Rescrape the product data
                    try:
                        response = scraper.get(product_url, headers=headers)
                        new_product_data = get_product_data(response.content)
                        
                        # Only update if we got new data
                        if new_product_data.get('brand') or new_product_data.get('product'):
                            # Merge the new data with existing data
                            product_data['brand'] = new_product_data['brand']
                            product_data['product'] = new_product_data['product']
                            
                            # Upload updated data back to S3
                            data_bytes = json.dumps(product_data).encode('utf-8')
                            file_obj = BytesIO(data_bytes)
                            s3_client.upload_fileobj(file_obj, bucket_name, file_path)
                            
                            print(f"Updated data for: {file_path}")
                            print(f"New brand: {new_product_data['brand']}")
                            print(f"New product: {new_product_data['product']}")
                        else:
                            print(f"No new data found for: {file_path}")
                            
                    except Exception as e:
                        print(f"Error rescraping {product_url}: {str(e)}")
                        
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

    return found_missing_data

def get_product_urls_from_sitemap(sitemap_number):
    """Extract product URLs from sitemap XML file stored in S3"""
    try:
        bucket_name = "product-buddy"
        sitemap_key = f"sitemap-scrapper/sitemap{sitemap_number}.xml"
        
        # Get sitemap file from S3
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=sitemap_key)
            sitemap_content = response['Body'].read()
        except ClientError as e:
            print(f"Error getting sitemap{sitemap_number}.xml from S3: {str(e)}")
            return []
        
        # Parse XML content directly from bytes
        root = ET.fromstring(sitemap_content)
        
        # Handle namespace
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        product_urls = []
        for url in root.findall('.//ns:url', ns):
            loc = url.find('ns:loc', ns)
            if loc is not None:
                url_str = loc.text
                # Check if it's a product URL (has /products/ and two more path components)
                if '/products/' in url_str:
                    parts = url_str.split('/products/')
                    if len(parts) == 2 and len(parts[1].split('/')) == 2:
                        # Convert full URL to relative path
                        relative_url = '/products/' + parts[1]
                        product_urls.append({
                            'product': {
                                'product_details': {
                                    'product_url': relative_url
                                }
                            }
                        })
        
        print(f"Found {len(product_urls)} product URLs in sitemap{sitemap_number}.xml")
        return product_urls
        
    except Exception as e:
        print(f"Error processing sitemap{sitemap_number}.xml: {str(e)}")
        return []

def lambda_handler(event, context):
    """Main handler that can be used for both Lambda and GitHub Actions"""
    sitemap_number = os.getenv('SITEMAP_NUMBER')
    if sitemap_number:
        sitemap_number = int(sitemap_number)
        print(f"Processing sitemap number: {sitemap_number}")
        
        # Get products from specific sitemap
        products = get_product_urls_from_sitemap(sitemap_number)
        print(f"Found {len(products)} products in sitemap {sitemap_number}")
    else:
        print("No sitemap number specified, processing all sitemaps")
        products = []
        for i in range(1, 7):
            sitemap_products = get_product_urls_from_sitemap(i)
            products.extend(sitemap_products)
    
    # Process the products using existing function
    scrape_and_upload_products(products)

def scrape_and_upload_products(products=None):
    """Main function to scrape and upload product data"""
    print("Starting product scraping...")
    
    # If no products provided, get from all sitemaps (backwards compatibility)
    if products is None:
        products = []
        for i in range(1, 7):
            try:
                sitemap_products = get_product_urls_from_sitemap(i)
                products.extend(sitemap_products)
            except Exception as e:
                print(f"Error loading sitemap {i}: {str(e)}")
    
    print(f"Total products to process: {len(products)}")
    
    # Continue with existing code
    s3_client = get_s3_client()
    bucket_name = "product-buddy"
    
    # Get count of existing products
    start_index = 0  # Reset to 0 since we're using new product list
    print(f"Starting from index: {start_index}")
    
    for number, product in enumerate(products[start_index:], start=start_index):
        try:
            url = product['product']['product_details']['product_url']
            product_url = url.strip('/')
            folder_path = product_url.lstrip('/')
            print(f"Processing product at path: {folder_path}")
            # Check if product file exists and has missing data
            try:
                product_file_path = f"{folder_path}/{folder_path.split('/')[-1]}.json"
                response = s3_client.get_object(Bucket=bucket_name, Key=product_file_path)
                
                
                # Skip if both brand and product exist and are not empty strings
            except:
                pass  # Product doesn't exist yet or other error, continue with scraping
            
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
            similar_products_response = scrapper.get(base_url + url + "/dupes", headers=headers)
            similar_data = get_similar_products(similar_products_response.content)
            # Get product data using the HTML content
            product_data = get_product_data(html_content)
            
            # Get pricing data using the same scraper and HTML content
            pricing_response = scrapper.get(base_url + url + "/vendors", headers=headers)
            pricing_data = get_product_pricing(pricing_response.content)
            
            # Get the product name from the URL for the file path
            product_name = folder_path.split('/')[-1]
            
            # Upload product data with new path structure
            upload_to_s3(s3_client, bucket_name, f"{folder_path}/{product_name}.json", product_data)
            upload_to_s3(s3_client, bucket_name, f"{folder_path}/pricing.json", pricing_data)
            upload_to_s3(s3_client, bucket_name, f"{folder_path}/similar_products.json", similar_data)
            
            # Get and upload image if available
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                image_tag = soup.find('img', {'fetchpriority': 'high'})
                
                if image_tag and image_tag.get('src'):
                    image_response = requests.get(image_tag['src'])
                    image_data = BytesIO(image_response.content)
                    s3_client.upload_fileobj(image_data, bucket_name, f"{folder_path}/{product_name}.jpg")
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
    product_header = soup.find('h1', class_='px-4')
    if product_header:
        # Find all span elements in the product header
        spans = product_header.find_all('span')
        
        if len(spans) >= 2:
            # First span contains the brand
            brand_link = spans[0].find('a')
            result["brand"] = brand_link.text.strip() if brand_link else spans[0].text.strip()
            
            # Second span contains the product name
            result["product"] = spans[1].text.strip()
            
            print(f"Found brand: {result['brand']}, product: {result['product']}")
        else:
            print(f"Expected 2 spans, found {len(spans)} in product header")
            result["brand"] = ""
            result["product"] = ""
    else:
        print("Product header not found")

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
        price_span = link.find('span', class_='text-sm')
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
    lambda_handler(None, None)
