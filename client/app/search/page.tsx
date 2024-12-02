'use client';
import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { SearchBar } from '../components/SearchBar';
import { ProductList } from '../components/ProductList';
import { Navbar } from '../components/Navbar';

interface Product {
  product: string;
  brand: string;
}

export default function SearchPage() {
  const searchParams = useSearchParams();
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
      console.log('Search results:', data);
      setSearchResults(data);
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to search products. Please try again.');
      setSearchResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle initial search from URL params
  useEffect(() => {
    const brand = searchParams.get('brand');
    const product = searchParams.get('product');
    
    if (brand && product) {
      handleSearch(brand, product);
    }
  }, [searchParams]);

  return (
    <div>
      <Navbar />
      <div className="min-h-screen bg-[#faf4f4]">
        <div className="max-w-4xl mx-auto px-4 py-12">
          <h1 className="text-4xl font-bold text-center mb-8 text-[#a984b2]">
            Search Products
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
    </div>
  );
} 