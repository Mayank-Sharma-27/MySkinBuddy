from langchain_community.utilities import GoogleSearchAPIWrapper
from typing import Dict, Any, List
import logging
from service.extractors.product_info_extractor import ProductInfoExtractor
import json
import boto3
from botocore.exceptions import ClientError

class ProductInformationAgent:
    def __init__(self):
        self.search_tool = GoogleSearchAPIWrapper()
        self.extractor = ProductInfoExtractor()
        self.s3_client = boto3.client('s3')
        self.bucket_name = "product-buddy"

    def get_product_info(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive product information from multiple sources and save to S3
        """
        try:
            print("=== Starting get_product_info ===")
            
            product_name = product_data['product']
            brand_name = product_data['brand']
            product_id = product_data['product_id']
            
            # Construct search query
            search_query = f"{brand_name} {product_name} skincare information"
            
            
            raw_results = self.search_tool.results(search_query, 5)
            
            search_results = [{
                'link': result['link'],
                'snippet': result['snippet'],
                'title': result['title']
            } for result in raw_results]
            # Parse and analyze results
            analyzed_results = self.extractor.analyze_top_results(search_results)
            
            aggregated_info = self.extractor.aggregate_information(analyzed_results)
            print("We got the aggregated info")
            # Aggregate information
            product_info = {
                'basic_info': {
                    'name': product_name,
                    'brand': brand_name,
                    'product_id': product_id
                },
                'detailed_info': aggregated_info,
                'sources': [result['link'] for result in search_results]
            }
            
            print(f"Final product info: {product_info}")
            
            # Save to S3
            self._save_to_s3(product_id, product_info)
            
            return product_info
            
        except Exception as e:
            print(f"=== Error in get_product_info ===")
            print(f"Error type: {type(e)}")
            print(f"Error message: {str(e)}")
            print(f"Product data: {product_data}")
            logging.exception("Detailed traceback:")
            raise

    def _save_to_s3(self, product_id: str, product_info: Dict[str, Any]) -> None:
        """
        Save product information to S3
        """
        try:
            # Construct the S3 key (path)
            s3_key = f"{product_id}/productDetail.json"
            
            # Convert dict to JSON string
            json_data = json.dumps(product_info, indent=2)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_data,
                ContentType='application/json'
            )
            
            print(f"Successfully saved product info to S3: {s3_key}")
            
        except ClientError as e:
            logging.error(f"Error saving to S3: {str(e)}")
            raise