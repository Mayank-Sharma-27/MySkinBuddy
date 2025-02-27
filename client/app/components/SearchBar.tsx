"use client";

import { useState } from "react";
import { ProductAutoComplete } from "./ProductAutocomplete";

interface SearchBarProps {
  onSearch: (productName: string, brandName: string) => void;
  userEmail?: string;
}

export function SearchBar({ onSearch, userEmail }: SearchBarProps) {
  const [searchMode, setSearchMode] = useState<"product" | "description">(
    "product"
  );

  return (
    <div className="w-full max-w-2xl mx-auto space-y-4">
      <div className="flex justify-center gap-4 text-sm">
        <button
          onClick={() => setSearchMode("product")}
          className={`px-4 py-2 rounded-full transition-all duration-200 ${
            searchMode === "product"
              ? "bg-primary-100 text-primary-700 font-medium"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          Search by Product
        </button>
        <button
          onClick={() => setSearchMode("description")}
          className={`px-4 py-2 rounded-full transition-all duration-200 ${
            searchMode === "description"
              ? "bg-primary-100 text-primary-700 font-medium"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          Describe Product
        </button>
      </div>

      <ProductAutoComplete
        onSearch={onSearch}
        isDescriptiveSearch={searchMode === "description"}
        placeholder={
          searchMode === "product"
            ? "Search any product..."
            : "Describe what you're looking for (e.g. 'vitamin c serum for brightening')..."
        }
        userEmail={userEmail}
      />
    </div>
  );
}
