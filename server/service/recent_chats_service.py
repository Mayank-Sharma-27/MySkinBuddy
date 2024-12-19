from typing import List, Dict
from .chat_service import get_recent_chats

def get_recent_chats(cookie_id: str, limit: int = 5) -> List[Dict]:
    """
    Fetch recent chats for a given cookie_id
    Returns list of chats with product info, ordered by most recent first
    """
    try:
        return get_recent_chats(cookie_id, limit)
    except Exception as e:
        print(f"Error fetching recent chats: {str(e)}")
        return []