"use client";

import { SearchBar } from "./components/SearchBar";
import { useRouter } from "next/navigation";
import { Navbar } from "./components/Navbar";
import RecentChats from "./components/RecentChats";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { useAuth } from "./contexts/AuthContext";

export default function Home() {
  const router = useRouter();
  const { isLoggedIn } = useAuth();

  const handleSearch = (productName: string, brandName: string) => {
    const params = new URLSearchParams();
    if (productName) params.append("product", productName);
    if (brandName) params.append("brand", brandName);

    router.push(`/product-search?${params.toString()}`);
  };

  return (
    <div>
      <Navbar />
      <main className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-4xl font-bold text-center text-[#a984b2] mb-12">
              Know Your Next Product
            </h1>

            <SearchBar onSearch={handleSearch} />
          </div>
        </div>

        {/* Only show RecentChats when logged in */}
        {isLoggedIn && <RecentChats />}
      </main>
    </div>
  );
}
