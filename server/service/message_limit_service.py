from service.auth import AuthService
from service.chat_service import ChatService

auth_service = AuthService()
chat_service = ChatService()

def check_message_limit(cookie_id: str) -> dict:
    """
    Shared service function to check if user has reached message limit
    Returns None if limit not reached, otherwise returns error dict
    """
    if not cookie_id:
        return {
            'error': 'Cookie ID is required',
            'requires_login': False,
            'message': 'Cookie ID is required'
        }

    user_email = auth_service.verify_cookie(cookie_id)
    if not user_email:  # User is not logged in
        message_count = chat_service.get_total_message_count(cookie_id)
        if message_count >= 10000:
            return {
                'error': 'Message limit reached',
                'requires_login': True,
                'message': 'Please login to continue using all features'
            }
    return None 