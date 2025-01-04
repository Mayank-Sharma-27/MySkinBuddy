# MySkinBuddy

MySkinBuddy is an intelligent skincare assistant that helps users discover and understand skincare products through natural conversation. It uses advanced AI to provide detailed information about ingredients, benefits, and product recommendations.

## Features

### Core Features

- **AI Skincare Assistant**: Intelligent chat-based skincare recommendations and advice
- **Product Search & Discovery**: Advanced search with auto-complete and filtering
- **User Authentication**: Secure login with email/password and Google OAuth
- **Chat History**: Persistent chat history and session management
- **Product Database**: Comprehensive skincare product and ingredient catalog

### Technical Features

- **Real-time Chat**: Interactive chat interface with streaming responses
- **Smart Recommendations**: AI-powered product suggestions based on skin type and concerns
- **Ingredient Analysis**: Detailed breakdown and compatibility checking
- **Vector Search**: Semantic search for products and ingredients
- **Multi-Agent System**: Specialized AI agents for different aspects of skincare

## Architecture

### Frontend (Next.js 14)

- TypeScript-based React components
- Tailwind CSS for styling
- Context-based state management
- Responsive and accessible design

### Backend (Flask 3.0)

- Python 3.9+ based REST API
- LangChain for AI/ML operations
- AWS S3 for data storage
- Pinecone for vector database

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- AWS Account
- Google OAuth credentials
- Pinecone Account
- OpenAI API key

### Environment Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/MySkinBuddy.git
   cd MySkinBuddy
   ```

2. Set up backend environment:

   ```bash
   cd server
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure backend environment variables:

   ```env
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_key
   GOOGLE_CLIENT_ID=your_key
   OPENAI_API_KEY=your_key
   PINECONE_API_KEY=your_key
   ```

4. Set up frontend environment:

   ```bash
   cd client
   npm install
   ```

5. Configure frontend environment variables:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8080
   NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id
   ```

### Running the Application

1. Start the backend server:

   ```bash
   cd server
   python -m flask run --port 8080
   ```

   The backend will be available at `http://localhost:8080`

2. Start the frontend development server:
   ```bash
   cd client
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`

## Project Structure

```
MySkinBuddy/
├── client/                 # Frontend Next.js application
│   ├── app/               # Next.js app directory
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts
│   │   ├── hooks/        # Custom hooks
│   │   └── utils/        # Utility functions
│   └── public/           # Static assets
├── server/                # Backend Flask application
│   ├── service/          # Business logic services
│   │   └── agents/       # AI agents
│   ├── views/            # API route handlers
│   └── scrapers/         # Data collection scripts
└── docs/                 # Documentation
    ├── frontend/         # Frontend documentation
    ├── backend/          # Backend documentation
    └── features/         # Feature documentation
```

## API Documentation

### Authentication Endpoints

- `POST /auth/google-login`: Google OAuth login
- `POST /auth/register`: User registration
- `POST /auth/login`: Email/password login
- `GET /auth/verify`: Token verification

### Chat Endpoints

- `POST /chat`: Send message to AI
- `GET /chat/history`: Get chat history
- `GET /recent-chats`: Get recent conversations

### Product Endpoints

- `GET /search-products`: Search products
- `GET /product-suggestions`: Get product suggestions
- `GET /products/<id>`: Get product details

## Development

### Code Style

- Python: PEP 8 guidelines
- TypeScript: ESLint + Prettier
- Git commit messages: Conventional Commits

### Testing

- Backend: Unit tests with pytest
- Frontend: React Testing Library
- E2E: Cypress

## Deployment

### Requirements

- Python 3.9+
- Node.js 18+
- AWS S3 bucket
- Pinecone instance
- Google OAuth credentials

### Configuration

- CORS settings
- Environment variables
- AWS IAM permissions

## Documentation

Detailed documentation is available in the `docs` directory:

- [Frontend Documentation](docs/frontend/README.md)
- [Backend Documentation](docs/backend/README.md)
- [Features Documentation](docs/features/README.md)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

Create Image command 
docker build -t myskinbuddy-backend .
Logoin

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 117669335220.dkr.ecr.us-east-1.amazonaws.com

Push the image

docker push 117669335220.dkr.ecr.us-east-1.amazonaws.com/myskinbuddy-backend:latest

New Deployment
aws ecs update-service --cluster myskinbuddy-cluster --service myskinbuddy-backend-8080 --force-new-deployment | cat




## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
