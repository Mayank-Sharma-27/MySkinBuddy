import { useState } from 'react';
import { SearchBar } from '../components/SearchBar';
import { ProductList } from '../components/ProductList';
import { Product } from '../types';

export default function SearchPage() {
  const [searchResults, setSearchResults] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
    } catch (err) {
      setError('Failed to search products. Please try again.');
      setSearchResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-pink-50 to-white">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold text-center mb-8 text-pink-800">
          MySkinBuddy
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Find your perfect skincare product
        </p>
        
        <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        
        {error && (
          <div className="text-red-500 text-center mt-4">
            {error}
          </div>
        )}
        
        <ProductList products={searchResults} />
      </div>
    </div>
  );
} 