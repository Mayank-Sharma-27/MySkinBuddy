from typing import List, Dict
from .chat_service import get_all_chats_from_s3

def get_recent_chats(cookie_id: str, limit: int = 5) -> List[Dict]:
    """
    Fetch recent chats for a given cookie_id
    Returns list of chats with product info, ordered by most recent first
    """
    try:
        all_chats = get_all_chats_from_s3(cookie_id)
        
        print(f"Recent chats: {all_chats}")
        # Filter only required fields
        simplified_chats = [{
            'chat_id': chat['chat_id'],
            'product': chat['product_name'],
            'brand': chat['brand_name'],
            'image_url': chat['image_url'],
            'product_id': chat['product_id']
        } for chat in all_chats]
        return simplified_chats[:limit]
    except Exception as e:
        print(f"Error fetching recent chats: {str(e)}")
        return []