"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useDebounce } from "../hooks/useDebounce";
import Image from "next/image";
import { getCookieId } from "../utils/cookies";
import { API_URL } from "../config";
import { useMessageLimit } from "../contexts/MessageLimitContext";
import dynamic from "next/dynamic";
import { SearchResult } from "../types";

const LoginModal = dynamic(() => import("./LoginModal"), {
  ssr: false,
});

interface Product {
  product_id: string;
  product: string;
  brand: string;
  image_url: string;
}

interface ProductAutoCompleteProps {
  onSearch: (productName: string, brandName: string) => void;
}

export function ProductAutoComplete({ onSearch }: ProductAutoCompleteProps) {
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const debouncedSearchTerm = useDebounce(query, 300);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const { showLoginPrompt, checkMessageLimit, resetLoginPrompt } =
    useMessageLimit();
  const [activeIndex, setActiveIndex] = useState<number>(-1);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setShowDropdown(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    const getSuggestions = async () => {
      if (!debouncedSearchTerm.trim()) {
        setProducts([]);
        return;
      }

      setIsLoading(true);
      try {
        // Check message limit before making the request
        const canProceed = await checkMessageLimit();
        if (!canProceed) {
          setProducts([]);
          return;
        }

        const response = await fetch(
          `${API_URL}/product-suggestions?q=${encodeURIComponent(
            debouncedSearchTerm
          )}`,
          {
            headers: {
              "X-Cookie-ID": getCookieId() || "",
            },
          }
        );

        if (response.status === 403) {
          const data = await response.json();
          if (data.requires_login) {
            setProducts([]);
            return;
          }
        }

        if (!response.ok) throw new Error("Search failed");
        const data = await response.json();
        setProducts(data);
        setShowDropdown(true);
      } catch (error) {
        setProducts([]);
      } finally {
        setIsLoading(false);
      }
    };

    getSuggestions();
  }, [debouncedSearchTerm, checkMessageLimit]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      const canProceed = await checkMessageLimit();
      if (!canProceed) return;

      onSearch(query, "");
      setShowDropdown(false);
      setQuery("");
    }
  };

  const handleProductSelect = async (product: Product) => {
    try {
      const canProceed = await checkMessageLimit();
      if (!canProceed) return;

      router.push(`/chat/${product.product_id}`);
    } catch (error) {
      // Handle error silently
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showDropdown) return;

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setActiveIndex((prev) =>
          prev < products.length - 1 ? prev + 1 : prev
        );
        break;
      case "ArrowUp":
        e.preventDefault();
        setActiveIndex((prev) => (prev > 0 ? prev - 1 : prev));
        break;
      case "Enter":
        e.preventDefault();
        if (activeIndex >= 0 && products[activeIndex]) {
          handleProductSelect(products[activeIndex]);
        }
        break;
      case "Escape":
        setShowDropdown(false);
        setActiveIndex(-1);
        break;
    }
  };

  return (
    <div className="relative">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Search any product..."
          className="w-full rounded-xl border-0 py-4 pl-4 pr-10 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-500 bg-white/70 backdrop-blur-sm"
        />
        <button
          onClick={handleSubmit}
          className="absolute inset-y-0 right-0 flex items-center px-4 text-gray-400 hover:text-primary-600 transition-colors"
        >
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </button>
      </div>

      {/* Suggestions dropdown */}
      {showDropdown && query.length > 0 && (
        <div className="absolute z-10 mt-2 w-full rounded-xl bg-white py-2 shadow-lg ring-1 ring-black ring-opacity-5">
          <div className="max-h-60 overflow-auto">
            {isLoading ? (
              <div className="p-4">
                <div className="animate-pulse flex flex-col gap-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="flex gap-4">
                      <div className="w-14 h-14 bg-gray-200 rounded-lg"></div>
                      <div className="flex-1 h-6 bg-gray-200 rounded-md"></div>
                    </div>
                  ))}
                </div>
              </div>
            ) : products.length > 0 ? (
              products.map((product, index) => (
                <div
                  key={product.product_id}
                  onClick={() => handleProductSelect(product)}
                  className={`cursor-pointer px-4 py-2 hover:bg-primary-50 ${
                    activeIndex === index ? "bg-primary-50" : ""
                  }`}
                  onMouseEnter={() => setActiveIndex(index)}
                >
                  <div className="font-medium text-gray-900">
                    {product.product}
                  </div>
                  {product.brand && (
                    <div className="text-sm text-gray-500">{product.brand}</div>
                  )}
                </div>
              ))
            ) : (
              <div className="p-6 text-center text-gray-500">
                No products found
              </div>
            )}
          </div>
        </div>
      )}

      {showLoginPrompt && (
        <LoginModal
          onClose={resetLoginPrompt}
          message="Please login to continue searching products"
        />
      )}
    </div>
  );
}
