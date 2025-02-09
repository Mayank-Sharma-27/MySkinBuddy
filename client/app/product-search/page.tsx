"use client";
export const dynamic = "force-dynamic";
export const revalidate = 0;

import { useRouter, useSearchParams } from "next/navigation";
import { useState, useEffect, useCallback } from "react";
import { Container } from "../components/ui/Container";
import Navbar from "../components/Navbar";
import { Footer } from "../components/Footer";
import { ProductAutoComplete } from "../components/ProductAutocomplete";
import { API_URL } from "../config";
import Image from "next/image";

interface Product {
  product_id: string;
  product: string;
  brand: string;
  image_url: string;
}

export default function ProductSearch() {
  const router = useRouter();
  const [searchResults, setSearchResults] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = useCallback(
    async (productName: string, brandName: string) => {
      const params = new URLSearchParams();
      if (productName) params.set("product", productName);
      if (brandName) params.set("brand", brandName);
      router.push(`/product-search?${params.toString()}`);

      // Fetch search results
      setIsLoading(true);
      try {
        const response = await fetch(
          `${API_URL}/product-suggestions?q=${encodeURIComponent(productName)}`
        );
        if (!response.ok) throw new Error("Search failed");
        const data = await response.json();
        setSearchResults(data);
      } catch (error) {
        setSearchResults([]);
      } finally {
        setIsLoading(false);
      }
    },
    [router]
  );

  const handleProductSelect = async (product: Product) => {
    try {
      router.push(`/chat/${product.product_id}`);
    } catch (error) {
      console.error("Error navigating to product:", error);
    }
  };

  return (
    <div>
      <Navbar />
      <main className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
              Search Products
            </h1>
            <ProductAutoComplete onSearch={handleSearch} />

            {/* Search Results */}
            {isLoading ? (
              <div className="mt-8">
                <div className="animate-pulse space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="flex gap-4 bg-white p-4 rounded-lg">
                      <div className="w-16 h-16 bg-gray-200 rounded-lg"></div>
                      <div className="flex-1 space-y-2">
                        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : searchResults.length > 0 ? (
              <div className="mt-8 space-y-4">
                {searchResults.map((product) => (
                  <div
                    key={product.product_id}
                    onClick={() => handleProductSelect(product)}
                    className="flex items-center gap-4 bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                  >
                    <Image
                      src={product.image_url}
                      alt={product.product}
                      width={64}
                      height={64}
                      className="rounded-lg"
                    />
                    <div>
                      <h3 className="font-medium text-gray-900">
                        {product.product}
                      </h3>
                      <p className="text-sm text-gray-500">{product.brand}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        </div>
      </main>
    </div>
  );
}
