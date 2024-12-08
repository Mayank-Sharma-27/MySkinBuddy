'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { ProductList } from '../components/ProductList';
import { SearchBar } from '../components/SearchBar';
import { getCookieId } from '../utils/cookies';

interface Product {
  product: string;
  brand: string;
  image_url: string;
}

export default function SearchPage() {
  const searchParams = useSearchParams();
  const productQuery = searchParams.get('product');
  const brandQuery = searchParams.get('brand');
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const fetchProducts = async () => {
      if (!productQuery && !brandQuery) return;
      
      setLoading(true);
      try {
        // Construct the query string based on available parameters
        const queryParams = new URLSearchParams();
        if (productQuery) queryParams.append('product_name', productQuery);
        if (brandQuery) queryParams.append('brand_name', brandQuery);
        
        const response = await fetch(`http://localhost:8080/search?${queryParams.toString()}`);
        
        if (!response.ok) {
          throw new Error('Search failed');
        }
        
        const data = await response.json();
        setProducts(data.products || []); // Assuming the API returns { products: [] }
      } catch (error) {
        console.error('Error searching products:', error);
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [productQuery, brandQuery]);

  const handleProductSelect = async (product: Product) => {
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
          product: product.product,
          brand: product.brand
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to start chat');
      }

      const data = await response.json();
      // After successful chat initialization, you might want to redirect to a chat page
      router.push(`/chat?id=${data.chat_id}`);
    } catch (error) {
      console.error('Error starting chat:', error);
      throw error;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-center text-[#a984b2] mb-8">
            Search Skincare Products
          </h1>
          
          <SearchBar />
          
          {loading ? (
            <div className="mt-8 text-center text-gray-600">
              <div className="animate-pulse">Searching products...</div>
            </div>
          ) : (
            <>
              {(productQuery || brandQuery) && (
                <div className="mt-6 mb-4 p-4 bg-white rounded-lg shadow-sm">
                  <h2 className="text-lg font-medium text-gray-700">
                    Search Results for:
                    {productQuery && <span className="text-[#a984b2]"> {productQuery}</span>}
                    {productQuery && brandQuery && ' by'}
                    {brandQuery && <span className="text-[#a984b2]"> {brandQuery}</span>}
                  </h2>
                </div>
              )}
              <div className="mt-4">
                <ProductList 
                  products={products} 
                  onProductSelect={handleProductSelect} 
                />
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
} 