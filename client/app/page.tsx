'use client';
import { useState } from 'react';
import { SearchBar } from './components/SearchBar';
import { ProductList } from './components/ProductList';
import { Navbar } from './components/Navbar';
import { useRouter } from 'next/navigation';

interface Product {
  product: string;
  brand: string;
}

interface ChatSession {
  chat_id: string;
  message: string;
}

export default function Home() {
  const [searchResults, setSearchResults] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [chatSession, setChatSession] = useState<ChatSession | null>(null);
  const router = useRouter();

  const handleSearch = async (brand: string, product: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `http://localhost:8080/search-products?brand=${encodeURIComponent(brand)}&product=${encodeURIComponent(product)}`
      );
      
      if (!response.ok) {
        throw new Error('Search failed');
      }
      
      const data = await response.json();
      setSearchResults(data);
      setHasSearched(true);
    } catch (err) {
      setError('Failed to search products. Please try again.');
      setSearchResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleProductSelect = async (product: Product) => {
    try {
      const response = await fetch('http://localhost:8080/start-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product: product.product,
          brand: product.brand
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to start chat');
      }

      const chatData = await response.json();
      
      // Navigate to chat page with parameters
      router.push(`/chat?chatId=${chatData.chat_id}&product=${encodeURIComponent(product.product)}&brand=${encodeURIComponent(product.brand)}&message=${encodeURIComponent(chatData.message)}`);
      
    } catch (error) {
      console.error('Failed to start chat:', error);
      // Handle error appropriately
    }
  };

  return (
    <main>
      <Navbar />
      <div className="min-h-screen bg-[#faf4f4]">
        <div className="max-w-4xl mx-auto px-4 py-12">
          {!hasSearched ? (
            <>
              <h1 className="text-5xl font-bold text-center mb-6 text-[#a984b2]">
                MySkinBuddy
              </h1>
              <p className="text-xl text-gray-600 mb-8 text-center">
                Your intelligent skincare assistant
              </p>
            </>
          ) : (
            <h1 className="text-4xl font-bold text-center mb-8 text-[#a984b2]">
              Search Results
            </h1>
          )}
          
          {!hasSearched && (
            <div className="max-w-2xl mx-auto">
              <SearchBar onSearch={handleSearch} isLoading={isLoading} />
            </div>
          )}
          
          {error && (
            <div className="text-red-500 text-center mt-4">
              {error}
            </div>
          )}
          
          {hasSearched && (
            <>
              <ProductList 
                products={searchResults} 
                onProductSelect={handleProductSelect}
              />
              <button
                onClick={() => {
                  setHasSearched(false);
                  setSelectedProduct(null);
                  setChatSession(null);
                }}
                className="mt-8 mx-auto block bg-[#a984b2] text-white px-6 py-2 rounded-lg hover:bg-[#8e6d97] transition-colors"
              >
                New Search
              </button>
            </>
          )}
          {selectedProduct && chatSession && (
            <ChatWindow
              chatId={chatSession.chat_id}
              initialMessage={chatSession.message}
              productName={selectedProduct.product}
              brandName={selectedProduct.brand}
              onClose={() => {
                setSelectedProduct(null);
                setChatSession(null);
              }}
            />
          )}
        </div>
      </div>
    </main>
  );
}
