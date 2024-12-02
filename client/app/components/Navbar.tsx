'use client';
import Link from 'next/link';

export function Navbar() {
  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link href="/" className="text-xl font-bold text-[#a984b2]">
            MySkinBuddy
          </Link>
          
          <div className="flex space-x-4">
            <Link 
              href="/" 
              className="text-gray-600 hover:text-[#a984b2] px-3 py-2"
            >
              Home
            </Link>
            <Link 
              href="/search" 
              className="text-gray-600 hover:text-[#a984b2] px-3 py-2"
            >
              Search
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
} 