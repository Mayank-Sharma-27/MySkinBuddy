# MySkinBuddy

MySkinBuddy is an intelligent skincare assistant that helps users discover and understand skincare products through natural conversation. It uses advanced AI to provide detailed information about ingredients, benefits, and product recommendations.

## Features

- **Product Search**: Search and discover skincare products by brand and name
- **Interactive Chat**: Have natural conversations about skincare products and their ingredients
- **Ingredient Analysis**: Get detailed information about skincare ingredients and their benefits
- **Smart Recommendations**: Receive personalized product suggestions based on skin concerns
- **Product Comparisons**: Compare different products and their ingredient compositions

## Technical Architecture

### Backend (Python/Flask)
- **Vector Database**: Pinecone for storing and retrieving product embeddings
- **LLM Integration**: Together AI for natural language processing
- **Storage**: AWS S3 for product and ingredient data storage

### Frontend (Next.js)
- **Real-time Chat**: Interactive chat interface with streaming responses
- **Product Search**: Dynamic product search with image display
- **Responsive Design**: Mobile-friendly interface

## Data Structure

### Product Data
- Product information
- Ingredient details
- Benefits and concerns
- Usage instructions

### Embeddings
- Product embeddings
- Ingredient embeddings
- Relationship mappings

## Setup

1. Clone the repository
2. Set up environment variables:
   ```
   TOGETHER_API_KEY=your_key
   PINECONE_API_KEY=your_key
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_key
   ```

3. Install dependencies:
   ```bash
   # Backend
   cd server
   pip install -r requirements.txt

   # Frontend
   cd client
   npm install
   ```

4. Run the development servers:
   ```bash
   # Backend
   python run.py

   # Frontend
   npm run dev
   ```

## API Endpoints

- `/search-products`: Search for products by name and brand
- `/chat`: Interactive product chat endpoint
- `/product-info`: Detailed product information

## Development Guidelines

- Use consistent code formatting
- Add appropriate type hints in Python code
- Follow React best practices for frontend components
- Document new API endpoints and features

## Future Enhancements

- Enhanced product comparison features
- Ingredient interaction analysis
- Personalized skincare routine recommendations
- Integration with e-commerce platforms

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details