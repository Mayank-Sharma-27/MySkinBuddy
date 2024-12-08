'use client';

import { useState } from 'react';

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
  const [productName, setProductName] = useState('');
  const [brandName, setBrandName] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (productName.trim() || brandName.trim()) {
      onSearch(productName.trim(), brandName.trim());
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <h1 className="text-center text-3xl font-semibold text-[#a984b2] mb-8">
        Search Skincare Products
      </h1>
      
      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm p-6">
        <div className="space-y-4">
          <div>
            <label htmlFor="product-name" className="block text-gray-700 mb-2">
              Product Name
            </label>
            <input
              id="product-name"
              type="text"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#a984b2] focus:border-transparent"
              placeholder="Enter product name..."
            />
          </div>
          
          <div>
            <label htmlFor="brand-name" className="block text-gray-700 mb-2">
              Brand Name
            </label>
            <input
              id="brand-name"
              type="text"
              value={brandName}
              onChange={(e) => setBrandName(e.target.value)}
              className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#a984b2] focus:border-transparent"
              placeholder="Enter brand name..."
            />
          </div>

          <button
            type="submit"
            className="w-full bg-[#a984b2] text-white p-3 rounded-lg hover:bg-[#8b6b94] transition-colors duration-200 flex items-center justify-center gap-2"
          >
            <SearchIcon />
            <span>Search Products</span>
          </button>
        </div>
      </form>
    </div>
  );
} 