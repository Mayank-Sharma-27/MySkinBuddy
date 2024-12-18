'use client';

import { useState, useEffect } from 'react';
import { useDebounce } from '../hooks/useDebounce';
import { useRouter } from 'next/navigation';
import { getCookieId } from '../utils/cookies';

interface Product {
  product: string;
  brand: string;
  image_url?: string;
}

interface ProductAutocompleteProps {
  onSelect?: (product: string, brand: string) => void;
  placeholder?: string;
}

export function ProductAutocomplete({ onSelect, placeholder = "Search for a product..." }: ProductAutocompleteProps) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<Product[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const debouncedQuery = useDebounce(query, 300);
  const router = useRouter();

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (debouncedQuery.length < 2) {
        setSuggestions([]);
        return;
      }

      setLoading(true);
      try {
        const response = await fetch(
          `http://localhost:8080/product-suggestions?query=${encodeURIComponent(debouncedQuery)}&max=5`
        );
        if (!response.ok) throw new Error('Failed to fetch suggestions');
        const data = await response.json();
        setSuggestions(data);
        setIsOpen(true);
      } catch (error) {
        console.error('Error fetching suggestions:', error);
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    };

    fetchSuggestions();
  }, [debouncedQuery]);

  const handleProductSelect = async (product: string, brand: string, imageUrl: string) => {
    try {
      const cookieId = getCookieId();
      if (!cookieId) {
        throw new Error('No cookie ID available');
      }

      const response = await fetch('http://localhost:8080/start-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Cookie-ID': cookieId
        },
        body: JSON.stringify({
          product: product,
          brand: brand
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to start chat');
      }

      const data = await response.json();
      
      const chatParams = new URLSearchParams({
        chatId: data.chat_id,
        product: encodeURIComponent(product),
        brand: encodeURIComponent(brand),
        message: data.message,
        imageUrl: encodeURIComponent(imageUrl)
      });

      router.push(`/chat?${chatParams.toString()}`);
    } catch (error) {
      console.error('Error starting chat:', error);
    }
  };

  return (
    <div className="relative w-full">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => setIsOpen(true)}
        className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#a984b2] focus:border-transparent"
        placeholder={placeholder}
      />
      
      {loading && (
        <div className="absolute right-3 top-3">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-[#a984b2]"></div>
        </div>
      )}

      {isOpen && suggestions.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white rounded-lg shadow-lg max-h-60 overflow-auto">
          {suggestions.map((suggestion, index) => (
            <div
              key={index}
              className="flex items-center p-3 hover:bg-gray-50 cursor-pointer"
              onClick={async () => {
                try {
                  await handleProductSelect(
                    suggestion.product, 
                    suggestion.brand,
                    suggestion.image_url || ''
                  );
                  setQuery('');
                  setIsOpen(false);
                } catch (error) {
                  console.error('Error handling product selection:', error);
                }
              }}
            >
              {suggestion.image_url && (
                <img 
                  src={suggestion.image_url} 
                  alt={`${suggestion.brand} - ${suggestion.product}`}
                  className="w-10 h-10 object-cover rounded-md mr-3"
                />
              )}
              <div>
                <div className="text-sm font-medium text-gray-900">{suggestion.product}</div>
                <div className="text-sm text-gray-500">{suggestion.brand}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 