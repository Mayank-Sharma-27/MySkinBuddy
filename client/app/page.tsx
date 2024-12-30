"use client";

import Navbar from "./components/Navbar";
import { Container } from "./components/ui/Container";
import { SearchBar } from "./components/SearchBar";
import { useRouter } from "next/navigation";
import { SearchIllustration } from "./components/illustrations/SearchIllustration";
import { ChatIllustration } from "./components/illustrations/ChatIllustration";
import { DiscoverIllustration } from "./components/illustrations/DiscoverIllustration";
import { Footer } from "./components/Footer";

export default function Home() {
  const router = useRouter();

  const handleSearch = (productName: string, brandName: string) => {
    const params = new URLSearchParams();
    if (productName) params.append("product", productName);
    if (brandName) params.append("brand", brandName);
    router.push(`/product-search?${params.toString()}`);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <div className="relative overflow-hidden bg-gray-50 min-h-[calc(100vh-4rem)]">
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary-50 to-secondary-50" />

          {/* Decorative blobs */}
          <div className="absolute top-0 left-0 -translate-x-1/2 translate-y-[-10%] w-96 h-96 bg-primary-200/30 rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-0 translate-x-1/3 translate-y-1/2 w-96 h-96 bg-secondary-200/30 rounded-full blur-3xl" />

          <Container className="relative">
            <div className="flex flex-col items-center justify-center pt-16 pb-24">
              <div className="text-center max-w-3xl mx-auto mb-16">
                <h1 className="text-5xl font-bold tracking-tight bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent mb-6">
                  Know Your Next Product
                </h1>
                <p className="text-xl text-gray-600 mb-10">
                  Discover skincare products tailored to your needs. Get
                  personalized recommendations and expert advice.
                </p>

                <div className="mb-16">
                  <SearchBar onSearch={handleSearch} />
                </div>
              </div>

              <div className="w-full max-w-6xl mx-auto">
                <h2 className="text-2xl font-semibold text-gray-900 text-center mb-12">
                  How it works
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                  {/* Step 1: Search */}
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 shadow-sm border border-gray-200/50">
                    <div className="relative w-full h-48 mb-6 rounded-lg overflow-hidden bg-white">
                      <SearchIllustration />
                    </div>
                    <div className="flex items-center gap-3 mb-4">
                      <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-600 font-semibold">
                        1
                      </span>
                      <h3 className="text-lg font-semibold text-gray-900">
                        Search Products
                      </h3>
                    </div>
                    <p className="text-gray-600">
                      Start by searching for any skincare product you're
                      interested in. Our smart search helps you find products
                      quickly with auto-suggestions.
                    </p>
                  </div>

                  {/* Step 2: Chat */}
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 shadow-sm border border-gray-200/50">
                    <div className="relative w-full h-48 mb-6 rounded-lg overflow-hidden bg-white">
                      <ChatIllustration />
                    </div>
                    <div className="flex items-center gap-3 mb-4">
                      <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-600 font-semibold">
                        2
                      </span>
                      <h3 className="text-lg font-semibold text-gray-900">
                        Chat with Product
                      </h3>
                    </div>
                    <p className="text-gray-600">
                      Have a conversation directly with the product. Ask about
                      ingredients, benefits, or how it fits your skin type and
                      concerns.
                    </p>
                  </div>

                  {/* Step 3: Discover */}
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 shadow-sm border border-gray-200/50">
                    <div className="relative w-full h-48 mb-6 rounded-lg overflow-hidden bg-white">
                      <DiscoverIllustration />
                    </div>
                    <div className="flex items-center gap-3 mb-4">
                      <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-600 font-semibold">
                        3
                      </span>
                      <h3 className="text-lg font-semibold text-gray-900">
                        Discover Similar
                      </h3>
                    </div>
                    <p className="text-gray-600">
                      Get recommendations for alternative products that might
                      work better for your specific needs and preferences.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </Container>
        </div>
      </main>
      <Footer />
    </div>
  );
}
