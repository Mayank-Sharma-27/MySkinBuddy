'use client';

import { ProductAutoComplete } from './ProductAutoComplete';

interface SearchBarProps {
  onSearch: (productName: string, brandName: string) => void;
}

export function SearchBar({ onSearch }: SearchBarProps) {
  return (
    <div className="w-full max-w-2xl mx-auto">
      <ProductAutoComplete onSearch={onSearch} />
    </div>
  );
} 