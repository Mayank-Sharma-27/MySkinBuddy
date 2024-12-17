'use client';

import { ProductAutocomplete } from './ProductAutocomplete';

interface SearchBarProps {
  onSearch: (productName: string, brandName: string) => void;
}

const SearchIcon = () => (
  <svg 
    xmlns="http://www.w3.org/2000/svg" 
    fill="none" 
    viewBox="0 0 24 24" 
    strokeWidth={1.5} 
    stroke="currentColor"
    className="w-5 h-5"
  >
    <path 
      strokeLinecap="round" 
      strokeLinejoin="round" 
      d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" 
    />
  </svg>
);

export function SearchBar({ onSearch }: SearchBarProps) {
  return (
    <div className="w-full max-w-2xl mx-auto">
      <h1 className="text-center text-3xl font-semibold text-[#a984b2] mb-8">
        Search Skincare Products
      </h1>
      
      <div className="bg-white rounded-xl shadow-sm p-6">
        <ProductAutocomplete 
          onSelect={(product, brand) => {
            onSearch(product, brand);
          }}
          placeholder="Search for skincare products..."
        />
      </div>
    </div>
  );
} 