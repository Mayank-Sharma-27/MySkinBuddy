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
    """
    Returns the singleton s3 client instance
    """
    return s3_client

# Fetch the webpage content

def get_products_url(url):
    response = requests.get(url)
    products_data = []
# Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the div with the specific ID
        div = soup.find('div', id='products-table')

        # Initialize a list to hold all product data

        try:

            # Iterate through each <h2> tag within the div
            for h2 in div.find_all('h2'):
                a_tags = h2.find_all('a')

                # Check if there are at least two <a> tags for brand and product
                if len(a_tags) >= 2:
                    # Get the first two <a> tags
                    brand_a, product_a = a_tags[:2]

                    # Extract brand details
                    brand_details = {
                        "brand_name": brand_a.text.strip(),
                        "brand_url": brand_a['href']
                    }

                    # Extract product details
                    product_details = {
                        "product_name": product_a.text.strip(),
                        "product_url": product_a['href']
                    }

                    # Append the combined product data to the products list
                    products_data.append({
                        "product": {
                            "brand_details": brand_details,
                            "product_details": product_details
                        }
                    })

        except:
            print("Unable to get data")

    return products_data
    # Define the name of the JSON file


def get_ingcredients(url):
    response = requests.get(url)


# Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

# Find the div with id 'ingredients-table'
    ingredients_div = soup.find('div', id='ingredients-table')


# Initialize a list to store the results
    ingredients_list = []

# Iterate through all 'a' tags within the div
    for a_tag in ingredients_div.find_all('a'):
        if a_tag.find("h4"):
            ingredient_info = {
                # Extract the URL from the href attribute
                'url': a_tag.get('href'),
                # Extract the name from the h4 tag
                'ingredient_name': a_tag.find('h4').text
            }
            ingredients_list.append(ingredient_info)

    return ingredients_list


def scrape_ingredient_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",
        "Connection": "keep-alive",
    }
    scrapper = cloudscraper.create_scraper()
    response = scrapper.get(url, headers= headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    explained_text = ""

    # Extract "Explained" section
    explained_section =  soup.select_one("div.mv-content.ingredient-description")
    if explained_section is not None and explained_section.text is not None:
        explained_text = ' '.join(
            [p.text for p in explained_section.find_all(['p', 'li'])])

    # Extract "Benefits"
    benefits_section = soup.select("div.flex.flex-wrap.mt-2 > div.rounded-full")
    benefits = []
    for benefit in benefits_section:
        benefit_text = benefit.find("div", class_="px-3 text-left py-0.5")
        if benefit_text:
            benefits.append(benefit_text.text.strip())

    # Extract "What it does"
    use = []
    what_it_does_heading = soup.find("h2", string=re.compile(r"\s*What it does\s*"))
    if what_it_does_heading:
        use_items = what_it_does_heading.find_next("div", class_="bg-white rounded-xl lg:max-w-sm").find_all("div", class_="border-b")
        for item in use_items:
            main_text = item.get_text(strip=True)
            additional_info = item.find("span", class_="text-xs text-warm-gray-700 py-2 font-normal")
            if additional_info:
                main_text += f" - {additional_info.text.strip()}"
            use.append(main_text)
            
    alt_names = []
    alt_names_heading = soup.find("h2", string=re.compile(r"\s*Alternative names\s*"))
    if alt_names_heading:
        alt_names_divs = alt_names_heading.find_next("div", class_="bg-white rounded-xl lg:max-w-sm").find_all("div", class_="border-b")
        alt_names = [div.get_text(strip=True) for div in alt_names_divs]
        
        # Extract "Concerns"
    concerns = []
    concerns_heading = soup.find("h3", string=re.compile(r"\s*Concerns\s*"))
    if concerns_heading:
    # Find the next container div after the "Concerns" heading
        concerns_section = concerns_heading.find_next("div", class_="flex flex-wrap mt-2")
        if concerns_section:
        # Loop through each div with the class 'rounded-full' within this section
            for concern in concerns_section.find_all("div", class_="rounded-full"):
            # Only select concerns that have the 'bg-red-100' class
                
                    concern_text = concern.find("div", class_="px-3 text-left py-0.5")
                    if concern_text:
                        concerns.append(concern_text.text.strip())

    
    # Structure data into a dictionary
    ingredient_data = {
        "Benefits": benefits,
        "Explained": explained_text,
        "use": use,
        "AltNames": alt_names,
        "Concerns": concerns
    }

    return ingredient_data


# scrape_ingredient_data("https://skinsort.com/ingredients/niacinamide")

def upload_ingredients():
    with open('ingredients.json', 'r') as file:
        ingredients = json.load(file)

        s3_client = get_s3_client()
        bucket_name = "product-buddy"
        folder = "ingredients"

    number = 0
    print(len(ingredients))
    for ingredient in ingredients:
        # Scrape data using the provided scrape_ingredient_data function
        number = number + 1
        if number > 23000:
            try:

            # Save the scraped data to a file
                file_name =f"{ingredient['ingredient_name']}".replace(
                    '\n', '').lower() + "/" + f"{ingredient['url']}.json".replace(
                    '\n', '').replace('ingredients', '').replace('/', '')
                    

                #data_bytes = json.dumps(data).encode('utf-8')
                #file_obj = BytesIO(data_bytes)
                s3_path = folder + "/" + f"{file_name}"
            # Upload the file to S3

                data = scrape_ingredient_data(
                    "https://skinsort.com" + ingredient['url'])
                data_bytes = json.dumps(data).encode('utf-8')
                file_obj = BytesIO(data_bytes)
                s3_client.upload_fileobj(file_obj, bucket_name,
                                             s3_path)

                print("Number of files uploaded : " + str(number))

            except Exception as e:
                print("Something went wrong while uploading" + str(e))

# Remember to replace 'your-s3-bucket-name' with your actual bucket name


# The ingredients_list now contains the desired information
list = []
# for i in range(1, 1152):

#    if i == 1:
#        url = 'https://skinsort.com/ingredients'

#    else:
#       url = "https://skinsort.com/ingredients/page/" + str(i)

#    print("number of products added " + str(8*i))

#    list.extend(get_ingcredients(url))


# with open('ingredients.json', 'w') as f:
#    json.dump(list, f)

# get_products_url("https://skinsort.com/products")

# def upload_all_products()
# upload_products()
def upload_products():
    for i in range(1, 1084):
        if i == 1:
            url = "https://skinsort.com/products"
            print("Page number added for :" + str(i))
        else:
            url = "https://skinsort.com/products/page/"+ str(i)
            print("Page number added for :" + str(i))

        list.extend(get_products_url(url))

    with open('products.json', 'w') as f:
        json.dump(list, f)


def get_product_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Send a GET request to the page
    response = requests.get(url, headers)

    # Initialize BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Initialize the result dictionary
    result = {
        "brand": "",
        "product": "",
        "ingredients_overview": [],
        "benefits": [],
        "concerns": []
    }

    # Find the ingredients section
    ingredients_section = soup.find(
        'div', class_='w-full my-3')
    if ingredients_section:
        for item in ingredients_section.find_all("div", class_='px-3 ml-3'):
            ingredient_element = item.find("div",
                                           class_='max-w-full break-words text-base')
            ingredient_name = ingredient_element.text.strip() if ingredient_element else None
            ingredient_url_element = item.find('a')
            ingredient_url = ingredient_url_element['href'] if ingredient_url_element and ingredient_url_element.has_attr(
                'href') else None
            ingredient_uses_element = item.find(
                class_='mt-1 flex flex-col lg:flex-row lg:items-center font-normal')
            ingredient_uses = ingredient_uses_element.text.strip(
            ) if ingredient_uses_element else None
            ingredient_info_element = item.find(class_='w-full pl-6 lg:pr-4')
            ingredient_info = ingredient_info_element.text.strip(
            ) if ingredient_info_element else None

            if ingredient_name:  # Only append if there's an ingredient name
                result['ingredients_overview'].append({
                    "ingredient_name": ingredient_name,
                    "ingredient_url": ingredient_url,
                    "ingredient_uses": ingredient_uses,
                    "ingredient_information": ingredient_info
                })

    # Find the benefits section
    parent_sections = soup.find_all(class_='flex flex-col justify-center')

    for section in parent_sections:
        # Check if this section has an <h3> with text 'Benefits', ignoring spaces
        h3 = section.find('h3')
        if h3 and ''.join(h3.text.split()).lower() == 'benefits':
            # Find elements with class 'flex flex-wrap mt-2 mb-2' within this section
            benefits_elements = section.find_all(
                class_='flex flex-wrap mt-2 mb-2')
            benefits_elements_names_elements = benefits_elements[0].find_all(
                "div")
            number = 0
            for element in benefits_elements_names_elements:
                # Find the first <span> within each element and extract its text
                first_span = element.find('span')
                benefit_name = first_span.text.strip() if first_span else None
                if benefit_name and benefit_name != 'Got it!':
                    if not any(benefit.get('benefit_name') == benefit_name for benefit in result['benefits']):
                        result['benefits'].append(
                            {"benefit_name": benefit_name})

    # Find the concerns section
    for section in parent_sections:
        # Check if this section has an <h3> with text 'Benefits', ignoring spaces
        h3 = section.find('h3')
        if h3 and ''.join(h3.text.split()).lower() == 'concerns':
            # Find elements with class 'flex flex-wrap mt-2 mb-2' within this section
            concern_elements = section.find_all(
                class_='flex flex-wrap mt-2 mb-2')
            concern_elements_names_elements = benefits_elements[0].find_all(
                "div")
            for element in concern_elements_names_elements:
                # Find the first <span> within each element and extract its text
                first_span = element.find('span')
                concern_name = first_span.text.strip() if first_span else None
                if concern_name and concern_name != 'Got it!':  # Only append if there's a benefit name
                    if not any(concern.get('concern_name') == concern_name for concern in result['concerns']):
                        result['concerns'].append(
                            {"concern_name": concern_name})
                        
        # Extract brand and product name
    product_header = soup.find('h1', class_='px-4 lg:px-0 break-words text-left leading-none tracking-tight text-warm-gray-800 text-2xl lg:text-5xl font-bold flex flex-col justify-center lg:justify-start')
    if product_header:
        # Extract the brand name
        brand_element = product_header.find('span', class_='pb-1 text-lg xl:text-3xl font-medium text-warm-gray-900/60')
        if brand_element:
            brand_link = brand_element.find('a')
            result["brand"] = brand_link.text.strip() if brand_link else ""

        # Extract the product name
        product_name = product_header.contents[1].strip() if len(product_header.contents) > 1 else ""
        result["product"] = product_name
                    

    return result


def upload_products_data():
    with open('products.json', 'r') as file:
        products = json.load(file)

        s3_client = get_s3_client()
        bucket_name = "skinsortdata"
        folder = "products"

    number = 0
    for product in products:
        # Scrape data using the provided scrape_ingredient_data function
        number = number + 1
        if number > 0:
            try:
                url = product['product']['product_details']['product_url']
                data = get_product_data(
                    "https://skinsort.com" + url)

            # Save the scraped data to a file
                file_name = f"{product['product']['product_details']['product_url']}.json".replace(
                    '\n', '')
                data_bytes = json.dumps(data).encode('utf-8')
                file_obj = BytesIO(data_bytes)
                s3_path = f"{file_name}"[1:]
                data_bytes = json.dumps(data).encode('utf-8')
                file_obj = BytesIO(data_bytes)
                s3_client.upload_fileobj(file_obj, bucket_name,
                                             s3_path)

                print("Number of files uploaded : " +
                          str(number) + " to path " + file_name)

            except Exception as e:
                print("Something went wrong while uploading" + str(e))

def upload_image_data():
    with open('products.json', 'r') as file:
        products = json.load(file)
        s3_client = get_s3_client()
        bucket_name = "product-buddy"
        number = 0  
        for product in products:
            number += 1
            if number > 3526:
                try:
                    headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                    }
                    product_url = product['product']['product_details']['product_url']
                    scrapper = cloudscraper.create_scraper()
                    response = scrapper.get("https://skinsort.com" + product_url)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    image_tag =  soup.find('img', {'fetchpriority': 'high'}) # Adjust as needed
                    image_url = image_tag['src'] if image_tag else None
    
                    if image_url:
                        image_response = requests.get(image_url)
                        image_data = BytesIO(image_response.content)
                        image_file_name = f"{product['product']['product_details']['product_url']}.jpg".replace('\n', '')
                        s3_path = f"{image_file_name}"[1:]
                        s3_client.upload_fileobj(image_data, bucket_name, s3_path)
                        print(f"Uploaded image for {product['product']['product_details']['product_name']} to {s3_path} number {number}")
                    else:
                        print(f"Image not found for {product['product']['product_details']['product_name']}")
                except Exception as e:
                    print(f"Error uploading image for {product['product']['product_details']['product_name']}: {str(e)}")

def upload_products_data():
    with open('products.json', 'r') as file:
        products = json.load(file)
        s3_client = get_s3_client()
        bucket_name = "skinsortdata"
        folder = "products"
 
        number = 0
        for product in products:
            number += 1
            if number > 3526:
                try:
                    url = product['product']['product_details']['product_url']
                    data = get_product_data("https://skinsort.com" + url)
                    file_name = f"{product['product']['product_details']['product_url']}.json".replace('\n', '')
                    data_bytes = json.dumps(data).encode('utf-8')
                    file_obj = BytesIO(data_bytes)
                    s3_path = f"{file_name}"[1:]
                    s3_client.upload_fileobj(file_obj, bucket_name, s3_path)
                    print("Number of files uploaded: " + str(number) + " to path " + file_name)
                except Exception as e:
                    print("Something went wrong while uploading: " + str(e))
 
# Call the upload functions
#upload_products_data()
#upload_image_data()

upload_ingredients()
