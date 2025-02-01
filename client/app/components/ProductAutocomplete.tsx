"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useDebounce } from "../hooks/useDebounce";
import Image from "next/image";
import { getCookieId } from "../utils/cookies";
import { API_URL } from "../config";
import { useMessageLimit } from "../contexts/MessageLimitContext";
import dynamic from "next/dynamic";

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

export const ProductAutoComplete = ({ onSearch }: ProductAutoCompleteProps) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const debouncedSearchTerm = useDebounce(searchTerm, 300);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const { showLoginPrompt, checkMessageLimit, resetLoginPrompt } =
    useMessageLimit();

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
    if (searchTerm.trim()) {
      const canProceed = await checkMessageLimit();
      if (!canProceed) return;

      onSearch(searchTerm, "");
      setShowDropdown(false);
      setSearchTerm("");
    }
  };

  const handleProductSelect = async (product: Product) => {
    try {
      const canProceed = await checkMessageLimit();
      if (!canProceed) return;

      const cookieId = getCookieId();
      if (!cookieId) {
        throw new Error("No cookie ID available");
      }

      const response = await fetch(`${API_URL}/start-chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Cookie-ID": cookieId,
        },
        body: JSON.stringify({
          product_id: product.product_id,
        }),
      });

      if (response.status === 403) {
        const data = await response.json();
        if (data.requires_login) return;
      }

      if (!response.ok) {
        throw new Error("Failed to start chat");
      }

      const data = await response.json();
      if (data.status === "success" && data.chat_data) {
        localStorage.setItem(
          `chat_data_${product.product_id}`,
          JSON.stringify(data.chat_data)
        );
        router.replace(`/chat/${product.product_id}`);
      } else {
        throw new Error(data.error || "Failed to start chat");
      }
    } catch (error) {
      // Remove console.error("Error starting chat:", error);
    }
  };

  return (
    <>
      <div className="relative w-full max-w-3xl mx-auto" ref={dropdownRef}>
        <form onSubmit={handleSubmit}>
          <div className="relative">
            <div className="absolute inset-y-0 flex items-center pointer-events-none">
              <svg
                className="h-5 w-5 text-gray-400"
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
            </div>
            <input
              ref={inputRef}
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onFocus={() => {
                setIsFocused(true);
                setShowDropdown(true);
              }}
              onBlur={() => setIsFocused(false)}
              placeholder="Search any product..."
              className={`w-full pl-8 pr-10 py-3.5 rounded-2xl border-2 bg-white/80 backdrop-blur-sm
                         transition-all duration-200 outline-none
                         ${
                           isFocused
                             ? "border-primary-300 shadow-lg shadow-primary-100/50"
                             : "border-gray-200 hover:border-gray-300"
                         }
                         placeholder:text-gray-400 placeholder:font-light
                         text-gray-900 text-base`}
            />
            {searchTerm && (
              <button
                type="button"
                onClick={() => {
                  setSearchTerm("");
                  inputRef.current?.focus();
                }}
                className="absolute inset-y-0 right-4 flex items-center"
              >
                <span className="sr-only">Clear search</span>
                <svg
                  className="h-5 w-5 text-gray-400 hover:text-gray-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            )}
          </div>
        </form>

        {showDropdown && searchTerm.length > 0 && (
          <div className="absolute z-10 left-0 right-0 mt-2 bg-white/80 backdrop-blur-sm rounded-xl shadow-xl border border-gray-100 overflow-hidden">
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
              products.map((product) => (
                <div
                  key={product.product_id}
                  onClick={() => handleProductSelect(product)}
                  className="flex items-center gap-3 p-3 cursor-pointer hover:bg-gray-100"
                >
                  <Image
                    src={product.image_url}
                    alt={product.product}
                    width={40}
                    height={40}
                    className="rounded-md"
                  />
                  <div className="flex flex-col">
                    <span className="font-medium text-gray-900">
                      {product.product}
                    </span>
                    <span className="text-sm text-gray-500">
                      {product.brand}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-4 text-gray-500">No products found.</div>
            )}
          </div>
        )}
      </div>

      {showLoginPrompt && (
        <LoginModal
          onClose={resetLoginPrompt}
          message="Please login to continue searching products"
        />
      )}
    </>
  );
};
