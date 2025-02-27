"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useDebounce } from "../hooks/useDebounce";
import Image from "next/image";
import { getCookieId } from "../utils/cookies";
import { API_URL } from "../config";
import dynamic from "next/dynamic";
import { SearchButton } from "./ui/SearchButton";
import { ImageUpload } from "./ImageUpload";

const LoginModal = dynamic(() => import("./LoginModal"), {
  ssr: false,
});

interface Product {
  label: string;
  value: {
    product: string;
    brand: string;
  };
  product_id: string;
  image_url: string;
  ingredients?: string[];
  benefits?: string[];
  concerns?: string[];
  subtitle?: string;
}

interface ProductAutoCompleteProps {
  onSearch: (productName: string, brandName: string) => void;
  initialSearchTerm?: string;
  disableInitialLoad?: boolean;
  isDescriptiveSearch?: boolean;
  placeholder?: string;
  userEmail?: string;
}

export const ProductAutoComplete = ({
  onSearch,
  initialSearchTerm = "",
  disableInitialLoad = false,
  isDescriptiveSearch = false,
  placeholder = "Search any product...",
  userEmail,
}: ProductAutoCompleteProps) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const debouncedSearchTerm = useDebounce(
    searchTerm,
    isDescriptiveSearch ? 500 : 300
  );
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const [activeIndex, setActiveIndex] = useState<number>(-1);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);
  const LIMIT = 5;

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
      if (
        isDescriptiveSearch ||
        !debouncedSearchTerm.trim() ||
        disableInitialLoad
      ) {
        setProducts([]);
        return;
      }

      setIsLoading(true);
      try {

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
  }, [
    debouncedSearchTerm,
    disableInitialLoad,
    isDescriptiveSearch,
  ]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      onSearch(searchTerm, "");
      setShowDropdown(false);
      setSearchTerm("");
    }
  };

  const handleProductSelect = async (product: Product) => {
    try {
      router.push(`/chat/${product.product_id}`);
    } catch (error) {
      // Handle error silently
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (isDescriptiveSearch) {
      if (e.key === "Enter") {
        e.preventDefault();
        handleSubmit(e as any);
      }
      return;
    }

    if (!showDropdown) {
      if (e.key === "Enter") {
        e.preventDefault();
        handleSubmit(e as any);
        return;
      }
    }

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
        } else {
          handleSubmit(e as any);
        }
        break;
      case "Escape":
        setShowDropdown(false);
        setActiveIndex(-1);
        break;
    }
  };

  const loadMoreSuggestions = async () => {
    if (!debouncedSearchTerm.trim() || isLoading) return;

    try {

      const response = await fetch(
        `${API_URL}/product-suggestions?q=${encodeURIComponent(
          debouncedSearchTerm
        )}&offset=${offset}&limit=${LIMIT}`,
        {
          headers: {
            "X-Cookie-ID": getCookieId() || "",
          },
        }
      );

      if (!response.ok) throw new Error("Search failed");
      const newProducts = await response.json();

      if (newProducts.length < LIMIT) {
        setHasMore(false);
      }

      setProducts((prev) => [...prev, ...newProducts]);
      setOffset((prev) => prev + LIMIT);
    } catch (error) {
      console.error("Error loading more suggestions:", error);
    }
  };

  useEffect(() => {
    setProducts([]);
    setOffset(1);
    setHasMore(true);
  }, [debouncedSearchTerm]);

  const handleTextExtracted = (text: string) => {
    setSearchTerm(text);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  return (
    <>
      <div className="relative w-full max-w-3xl mx-auto" ref={dropdownRef}>
        <form onSubmit={handleSubmit}>
          <div className="relative">
            <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
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
              onKeyDown={handleKeyDown}
              onFocus={() => {
                setIsFocused(true);
                if (!isDescriptiveSearch) {
                  setShowDropdown(true);
                }
              }}
              onBlur={() => {
                setIsFocused(false);
                if (!isDescriptiveSearch) {
                  setTimeout(() => setShowDropdown(false), 200);
                }
              }}
              placeholder={placeholder}
              className={`w-full pl-10 pr-16 py-4 rounded-2xl border-2 bg-white/80 
                       backdrop-blur-sm transition-all duration-200 outline-none
                       text-base md:text-lg
                       shadow-sm focus:shadow-lg
                       ${
                         isFocused
                           ? "border-primary-300 shadow-primary-100/50"
                           : "border-gray-200 hover:border-gray-300"
                       }
                       placeholder:text-gray-400 placeholder:font-light
                       text-gray-900`}
              role={isDescriptiveSearch ? "searchbox" : "combobox"}
              aria-expanded={!isDescriptiveSearch && showDropdown}
              aria-controls={
                !isDescriptiveSearch ? "search-listbox" : undefined
              }
              aria-activedescendant={
                !isDescriptiveSearch && activeIndex >= 0
                  ? `option-${activeIndex}`
                  : undefined
              }
            />
            {searchTerm && (
              <button
                type="button"
                onClick={() => {
                  setSearchTerm("");
                  inputRef.current?.focus();
                }}
                className="absolute right-14 inset-y-0 flex items-center pr-2"
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
            <button
              type="submit"
              className="absolute inset-y-0 right-4 flex items-center"
            >
              <span className="sr-only">Search</span>
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
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </button>
          </div>
        </form>

        {!isDescriptiveSearch && (
          <div className="mt-4">
            <ImageUpload
              onTextExtracted={handleTextExtracted}
              userEmail={userEmail}
            />
          </div>
        )}

        {!isDescriptiveSearch && showDropdown && searchTerm.length > 0 && (
          <div
            className="absolute z-10 left-0 right-0 mt-2 bg-white/80 backdrop-blur-sm 
                     rounded-xl shadow-xl border border-gray-100
                     transition-all duration-200 ease-in-out
                     max-h-[400px] overflow-y-auto"
            role="listbox"
            id="search-listbox"
            onScroll={(e) => {
              const target = e.target as HTMLDivElement;
              if (
                target.scrollHeight - target.scrollTop ===
                  target.clientHeight &&
                hasMore &&
                !isLoading
              ) {
                loadMoreSuggestions();
              }
            }}
          >
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
                  className={`flex items-center gap-4 p-3 cursor-pointer
                           transition-colors duration-150 ease-in-out
                           hover:bg-primary-50/50 active:bg-primary-50
                           ${activeIndex === index ? "bg-primary-50/50" : ""}
                           ${
                             index !== products.length - 1
                               ? "border-b border-primary-100"
                               : ""
                           }`}
                  role="option"
                  id={`option-${index}`}
                  aria-selected={activeIndex === index}
                >
                  <div className="flex-shrink-0 w-16 h-16 sm:w-14 sm:h-14 relative">
                    <Image
                      src={product.image_url}
                      alt={product.value.product}
                      fill
                      className="rounded-lg object-contain bg-white p-0.5"
                      sizes="(max-width: 768px) 64px, 56px"
                      priority={index < 4}
                    />
                  </div>
                  <div className="flex flex-col min-w-0 flex-1">
                    <span className="text-sm font-medium text-primary-600 line-clamp-1">
                      {product.value.brand}
                    </span>
                    <span className="text-base font-semibold text-primary-900 line-clamp-1">
                      {product.value.product}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-6 text-center text-gray-500">
                No products found
              </div>
            )}
            {hasMore && (
              <div className="p-4 text-center">
                <span className="text-gray-500">Loading more...</span>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
};
