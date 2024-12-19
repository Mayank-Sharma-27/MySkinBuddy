"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ProductList } from "../components/ProductList";
import { getCookieId } from "../utils/cookies";
import { Navbar } from "../components/Navbar";

interface Product {
  product: string;
  brand: string;
  image_url: string;
}

export default function ProductSearchPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const params = new URLSearchParams();
        const productName = searchParams.get("product");
        const brandName = searchParams.get("brand");

        if (productName) params.append("product", productName);
        if (brandName) params.append("brand", brandName);

        const response = await fetch(
          `http://localhost:8080/search-products?${params.toString()}`
        );
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Search failed");
        }

        const data = await response.json();
        setProducts(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error("Error searching products:", error);
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [searchParams]);

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
          'X-Cookie-ID': cookieId,
        },
        body: JSON.stringify({
          product_id: product.product_id,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to start chat');
      }

      const data = await response.json();
      if (data.status === 'success') {
        router.push(`/chat/${product.product_id}?chat_id=${data.chat_id}`);
      } else {
        throw new Error(data.error || 'Failed to start chat');
      }
    } catch (error) {
      console.error('Error starting chat:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {loading ? (
            <div className="text-center text-gray-600">
              <div className="animate-pulse">Loading products...</div>
            </div>
          ) : products.length > 0 ? (
            <ProductList
              products={products}
              onProductSelect={handleProductSelect}
            />
          ) : (
            <div className="text-center text-gray-600">
              No products found. Try adjusting your search terms.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
