from typing import List, Dict
from .chat_service import ChatService

chat_service = ChatService()

def get_recent_chats(cookie_id: str, limit: int = 5) -> List[Dict]:
    """
    Fetch recent chats for a given cookie_id
    Returns list of unique chats with product info, ordered by most recent first
    """
    try:
        all_chats = chat_service.get_all_chats_from_s3(cookie_id)
        print(f"All chats: {all_chats}")
        # Transform chats to only include required fields
        recent_chats = []
        seen_products = set()
        
        for chat in all_chats:
            product_id = chat.get('product_id')
            if product_id and product_id not in seen_products:
                seen_products.add(product_id)
                recent_chats.append({
                    'product_name': chat['product_name'],
                    'image_url': chat['image_url'],
                    'product_id': product_id,
                    'brand_name': chat['brand_name']  
                })
                
                if len(recent_chats) >= limit:
                    break
                    
        return recent_chats
    except Exception as e:
        print(f"Error fetching recent chats: {str(e)}")
        return []