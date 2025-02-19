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
import { getCookieId } from "../utils/cookies";

interface Product {
  product_id: string;
  product: string;
  brand: string;
  image_url: string;
}

export default function ProductSearch() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [searchResults, setSearchResults] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const productQuery = searchParams.get("product");
  const [initialSearchTerm, setInitialSearchTerm] = useState("");
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);
  const LIMIT = 20;

  useEffect(() => {
    if (productQuery) {
      setInitialSearchTerm(decodeURIComponent(productQuery));
      setHasMore(true);
      performSearch(productQuery, true);
    }
  }, [productQuery]);

  const performSearch = async (query: string, isInitial: boolean = false) => {
    setIsLoading(true);
    try {
      const currentOffset = isInitial ? 0 : offset;

      const response = await fetch(
        `${API_URL}/search-products?product=${encodeURIComponent(
          query
        )}&offset=${currentOffset}&limit=${LIMIT}`,
        {
          headers: {
            "X-Cookie-ID": getCookieId() || "",
          },
        }
      );

      if (!response.ok) throw new Error("Search failed");
      const data = await response.json();

      if (data.length < LIMIT) {
        setHasMore(false);
      }

      setSearchResults((prev) => (isInitial ? data : [...prev, ...data]));
      setOffset((prev) => currentOffset + LIMIT);
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (productName: string, brandName: string) => {
    const params = new URLSearchParams();
    if (productName) params.set("product", productName);
    if (brandName) params.set("brand", brandName);
    router.push(`/product-search?${params.toString()}`);
  };

  const handleProductSelect = async (product: Product) => {
    try {
      router.push(`/chat/${product.product_id}`);
    } catch (error) {
      console.error("Error navigating to product:", error);
    }
  };

  const debounce = (func: (...args: any[]) => void, wait: number) => {
    let timeoutId: ReturnType<typeof setTimeout>;

    const debounced = (...args: Parameters<typeof func>) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func(...args), wait);
    };

    debounced.cancel = () => {
      clearTimeout(timeoutId);
    };

    return debounced;
  };

  useEffect(() => {
    const handleScroll = () => {
      if (
        window.innerHeight + window.scrollY >=
          document.documentElement.scrollHeight - 100 &&
        hasMore &&
        !isLoading &&
        searchParams.get("product")
      ) {
        performSearch(searchParams.get("product")!);
      }
    };

    const debouncedHandleScroll = debounce(handleScroll, 100);

    window.addEventListener("scroll", debouncedHandleScroll);
    return () => {
      window.removeEventListener("scroll", debouncedHandleScroll);
      debouncedHandleScroll.cancel();
    };
  }, [hasMore, isLoading, offset, searchParams]);

  return (
    <div>
      <Navbar />
      <main className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 sm:px-6 py-6 sm:py-8">
          <div className="max-w-3xl mx-auto">
            <h1 className="text-xl sm:text-2xl font-semibold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent mb-6 sm:mb-8 text-center">
              {productQuery
                ? `Search results for "${productQuery}"`
                : "Search Products"}
            </h1>
            <ProductAutoComplete
              onSearch={handleSearch}
              disableInitialLoad={!!productQuery}
            />

            {/* Search Results */}
            <div className="mt-8 space-y-4">
              {searchResults.map((product) => (
                <div
                  key={product.product_id}
                  onClick={() => handleProductSelect(product)}
                  className="flex flex-col sm:flex-row gap-4 sm:gap-6 bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer relative"
                >
                  <div className="mx-auto sm:mx-0 w-48 h-48 sm:w-32 sm:h-32 relative">
                    <Image
                      src={product.image_url}
                      alt={product.product}
                      fill
                      className="rounded-lg object-contain"
                      sizes="(max-width: 640px) 192px, 128px"
                    />
                  </div>
                  <div className="flex-1">
                    <div className="flex flex-col sm:flex-row justify-between items-center sm:items-start text-center sm:text-left">
                      <div>
                        <div className="text-base text-gray-600 font-medium">
                          {product.brand}
                        </div>
                        <h3 className="text-lg font-semibold text-primary-600 mt-1">
                          {product.product}
                        </h3>
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {/* Loading indicator at the bottom */}
              {isLoading && (
                <div className="animate-pulse space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div
                      key={`loading-${i}`}
                      className="flex flex-col sm:flex-row gap-4 sm:gap-6 bg-white p-4 rounded-lg"
                    >
                      <div className="mx-auto sm:mx-0 w-48 h-48 sm:w-32 sm:h-32 bg-gray-200 rounded-lg"></div>
                      <div className="flex-1 space-y-2 text-center sm:text-left">
                        <div className="h-5 bg-gray-200 rounded w-24 mx-auto sm:mx-0"></div>
                        <div className="h-6 bg-gray-200 rounded w-3/4 mx-auto sm:mx-0"></div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* No results message */}
              {!isLoading && searchResults.length === 0 && productQuery && (
                <div className="text-center text-gray-500">
                  No products found for "{productQuery}"
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
