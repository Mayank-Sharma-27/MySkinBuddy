"use client";

import { useSearchParams } from "next/navigation";
import { Navbar } from "../components/Navbar";
import ProductChat from "../components/ProductChat";

export default function ProductSearch() {
  const searchParams = useSearchParams();
  const productName = searchParams.get("product");
  const brandName = searchParams.get("brand");

  return (
    <div>
      <Navbar />
      <main className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <ProductChat
            productName={productName || ""}
            brandName={brandName || ""}
          />
        </div>
      </main>
    </div>
  );
}
