# Backend Documentation

## Technology Stack

### Core Technologies

- **Framework**: Flask 3.0.2
- **Language**: Python 3.9+
- **CORS**: Flask-CORS 4.0.0
- **Environment**: python-dotenv 1.0.0

### AI & Machine Learning

- **LangChain**: v0.3.6
  - langchain-openai
  - langchain-together
  - langchain-pinecone
  - langchain-community
- **Vector Database**: Pinecone
- **Tokenizer**: tiktoken

### Cloud Services

- **Storage**: AWS S3 (boto3)
- **Authentication**: Google Auth

## Architecture Overview

### Core Components

1. **Application Entry (app.py)**

   ```python
   from flask import Flask
   from flask_cors import CORS

   app = Flask(__name__)
   CORS(app, resources={
       r"/recent-chats": {"origins": ["http://localhost:3000"]},
       r"/search-products": {"origins": ["http://localhost:3000"]},
       # ... other routes
   })
   ```

   - CORS configuration
   - Route registration
   - Application initialization

2. **Environment Configuration**
   - `.env` file management
   - Secure credential storage
   - Environment-specific settings

## Services

### Authentication Service (auth.py)

```python
class AuthService:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.cookie_service = CookieService()
```

- Google OAuth integration
- JWT token management
- Password hashing and verification
- Session management
- S3-based user data storage

### Chat Service (chat_service.py)

```python
def save_chat(cookie_id: str, product_id: str, chat_data: dict):
    """Save chat data to S3"""
    key = f"chats/{cookie_id}/{product_id}.json"
    # Implementation...
```

Features:

- Real-time chat processing
- Chat history persistence
- Message count tracking
- Multi-agent coordination

### Product Service (product_service.py)

- Product database management
- Search functionality
- Product recommendations
- Category management

### Cookie Service (cookie_service.py)

- Session tracking
- User identification
- Security measures
- Cookie management

## AI Agents

### Product Information Agent

- Product details analysis
- Feature extraction
- Specification processing

### Ingredients Analyzer Agent

- Ingredient breakdown
- Safety analysis
- Compatibility checking

### Product Recommendations Agent

- Personalized suggestions
- Similar product matching
- Usage pattern analysis

## Data Storage

### S3 Structure

```
bucket/
├── users/
│   └── {user_id}/
│       └── profile.json
├── chats/
│   └── {cookie_id}/
│       └── {product_id}.json
└── products/
    └── catalog.json
```

### Data Models

- User profiles
- Chat histories
- Product information
- Authentication records

## API Endpoints

### Authentication Routes

```python
@app.route('/auth/google-login', methods=['POST'])
@app.route('/auth/register', methods=['POST'])
@app.route('/auth/login', methods=['POST'])
@app.route('/auth/verify', methods=['GET'])
```

### Chat Routes

```python
@app.route('/chat', methods=['POST'])
@app.route('/chat/history', methods=['GET'])
@app.route('/recent-chats', methods=['GET'])
```

### Product Routes

```python
@app.route('/search-products', methods=['GET'])
@app.route('/product-suggestions', methods=['GET'])
@app.route('/products/<id>', methods=['GET'])
```

## Security

### Authentication

- Google OAuth 2.0
- JWT token validation
- Password encryption
- Session management

### Data Protection

- Environment variable security
- S3 bucket policies
- CORS configuration
- Rate limiting

## Performance Optimization

### Caching

- Response caching
- Product data caching
- Session caching

### Concurrent Processing

```python
executor = ThreadPoolExecutor(max_workers=3)
# Parallel agent execution
```

### Database Optimization

- Efficient queries
- Connection pooling
- Index optimization

## Development

### Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables

```env
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
GOOGLE_CLIENT_ID=
OPENAI_API_KEY=
PINECONE_API_KEY=
```

### Project Structure

```
server/
├── app.py
├── requirements.txt
├── service/
│   ├── auth.py
│   ├── chat_service.py
│   ├── product_service.py
│   └── agents/
├── views/
│   ├── auth_view.py
│   ├── chat_view.py
│   └── product_view.py
└── scrapers/
```

## Testing

### Unit Tests

- Service layer testing
- Agent testing
- Utility function testing

### Integration Tests

- API endpoint testing
- Authentication flow testing
- Data persistence testing

### Load Testing

- Concurrent request handling
- Response time monitoring
- Resource usage tracking

## Deployment

### Prerequisites

- Python 3.9+
- AWS credentials
- Google OAuth setup
- Pinecone account

### Configuration

- Environment setup
- CORS configuration
- Service initialization

### Monitoring

- Error logging
- Performance metrics
- Usage statistics
