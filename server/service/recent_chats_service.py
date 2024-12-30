from typing import List, Dict
from .chat_service import get_all_chats_from_s3

def get_recent_chats(cookie_id: str, limit: int = 5) -> List[Dict]:
    """
    Fetch recent chats for a given cookie_id
    Returns list of unique chats with product info, ordered by most recent first
    """
    try:
        all_chats = get_all_chats_from_s3(cookie_id)
        
        # Keep track of seen product_ids
        seen_products = set()
        unique_chats = []
        
        for chat in all_chats:
            product_id = chat.get('product_id')
            if product_id and product_id not in seen_products:
                seen_products.add(product_id)
                unique_chats.append({
                    'product': chat['product_name'],
                    'brand': chat['brand_name'],
                    'image_url': chat['image_url'],
                    'product_id': product_id
                })
                
                if len(unique_chats) >= limit:
                    break
                    
        return unique_chats
    except Exception as e:
        print(f"Error fetching recent chats: {str(e)}")
        return []