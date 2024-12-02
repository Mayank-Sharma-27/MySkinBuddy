'use client';
import { useState } from 'react';

interface SearchBarProps {
  onSearch: (brand: string, product: string) => void;
  isLoading: boolean;
}

export function SearchBar({ onSearch, isLoading }: SearchBarProps) {
  const [brand, setBrand] = useState('');
  const [product, setProduct] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (brand && product) {
      onSearch(brand, product);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="flex flex-col md:flex-row gap-4">
        <input
          type="text"
          placeholder="Enter brand name..."
          value={brand}
          onChange={(e) => setBrand(e.target.value)}
          className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#a984b2]"
          disabled={isLoading}
        />
        <input
          type="text"
          placeholder="Enter product name..."
          value={product}
          onChange={(e) => setProduct(e.target.value)}
          className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#a984b2]"
          disabled={isLoading}
        />
      </div>
      
      <button
        type="submit"
        disabled={!brand || !product || isLoading}
        className={`w-full p-3 rounded-lg text-white transition-colors
          ${isLoading || !brand || !product 
            ? 'bg-gray-400 cursor-not-allowed' 
            : 'bg-[#a984b2] hover:bg-[#8e6d97]'
          }`}
      >
        {isLoading ? 'Searching...' : 'Search'}
      </button>
    </form>
  );
} 