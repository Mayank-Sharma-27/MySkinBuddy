"use client";
import { useState, useRef, useEffect, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useDebounce } from "../hooks/useDebounce";
import Image from "next/image";
import { getCookieId } from "../utils/cookies";

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
  const debouncedSearchTerm = useDebounce(searchTerm, 300);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

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
        const response = await fetch(
          `http://localhost:8080/product-suggestions?q=${encodeURIComponent(
            debouncedSearchTerm
          )}`
        );
        if (!response.ok) throw new Error("Search failed");
        const data = await response.json();
        setProducts(data);
      } catch (error) {
        console.error("Error getting suggestions:", error);
        setProducts([]);
      } finally {
        setIsLoading(false);
      }
    };

    getSuggestions();
  }, [debouncedSearchTerm]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      onSearch(searchTerm, "");
      setShowDropdown(false);
    }
  };

  const handleProductSelect = async (product: Product) => {
    try {
      const cookieId = getCookieId();
      if (!cookieId) {
        throw new Error("No cookie ID available");
      }

      const response = await fetch("http://localhost:8080/start-chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Cookie-ID": cookieId,
        },
        body: JSON.stringify({
          product_id: product.product_id,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to start chat");
      }

      const data = await response.json();
      if (data.status === "success") {
        localStorage.setItem(`chat_data_${data.chat_data.chat_id}`, JSON.stringify(data.chat_data));
        router.push(`/chat/${product.product_id}?chat_id=${data.chat_data.chat_id}`);
      } else {
        throw new Error(data.error || "Failed to start chat");
      }
    } catch (error) {
      console.error("Error starting chat:", error);
    }
  };

  return (
    <div className="relative w-full" ref={dropdownRef}>
      <form onSubmit={handleSubmit} className="flex">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onFocus={() => setShowDropdown(true)}
          placeholder="Search for a product..."
          className="w-full p-4 border border-gray-300 rounded-l-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-[#a984b2] focus:border-transparent"
        />
        <button
          type="submit"
          className="px-6 bg-[#a984b2] text-white rounded-r-lg hover:bg-[#8e6d97] transition-colors"
        >
          Search
        </button>
      </form>

      {showDropdown && searchTerm.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white rounded-lg shadow-lg max-h-96 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 text-gray-500">Loading...</div>
          ) : products.length > 0 ? (
            <div className="py-2">
              {products.map((product) => (
                <div
                  key={product.product_id}
                  onClick={() => handleProductSelect(product)}
                  className="flex items-center gap-4 px-4 py-2 hover:bg-gray-50 cursor-pointer"
                >
                  <div className="relative w-12 h-12 flex-shrink-0">
                    <Image
                      src={product.image_url || "/placeholder-product.png"}
                      alt={product.product}
                      fill
                      className="object-cover rounded"
                      sizes="48px"
                    />
                  </div>
                  <div>
                    <div className="font-medium text-gray-800">
                      {product.product}
                    </div>
                    <div className="text-sm text-gray-500">{product.brand}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-4 text-gray-500">No products found</div>
          )}
        </div>
      )}
    </div>
  );
};
