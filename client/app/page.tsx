"use client";

import Navbar from "./components/Navbar";
import { Container } from "./components/ui/Container";
import { SearchBar } from "./components/SearchBar";
import { useRouter } from "next/navigation";
import { Footer } from "./components/Footer";
import { useEffect, useState } from "react";
import { useCookie } from "./utils/CookieProvider";
import { API_URL } from "./config";
import RecentChats from "./components/RecentChats";
import { HowItWorks } from "./components/HowItWorks";

interface Chat {
  id: string;
  product_name: string;
  last_message: string;
  timestamp: string;
}

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default function Home() {
  const router = useRouter();
  const cookieId = useCookie();
  const [hasRecentChats, setHasRecentChats] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkRecentChats = async () => {
      if (!cookieId) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch(`${API_URL}/recent-chats`, {
          headers: {
            "X-Cookie-ID": cookieId,
          },
        });

        const data = await response.json();
        if (data.status === "success" && data.chats && data.chats.length > 0) {
          setHasRecentChats(true);
        }
      } catch (error) {
        console.error("Error checking recent chats:", error);
      } finally {
        setIsLoading(false);
      }
    };

    checkRecentChats();
  }, [cookieId]);

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
                  Welcome to MyGlowPal
                </h1>
                <p className="text-xl text-gray-600 mb-10">
                  Ask questions directly to your skincare products.
                </p>

                <div className="relative w-full max-w-2xl mx-auto mb-10">
                  <div
                    className="absolute inset-0 -z-10 transform-gpu blur-2xl"
                    aria-hidden="true"
                  >
                    <div
                      className="aspect-[577/310] w-[36.0625rem] bg-gradient-to-r from-primary-500 to-secondary-500 opacity-30"
                      style={{
                        clipPath:
                          "polygon(74.8% 41.9%, 97.2% 73.2%, 100% 34.9%, 92.5% 0.4%, 87.5% 0%, 75% 28.6%, 58.5% 54.6%, 50.1% 56.8%, 46.9% 44%, 48.3% 17.4%, 24.7% 53.9%, 0% 27.9%, 11.9% 74.2%, 24.9% 54.1%, 68.6% 100%, 74.8% 41.9%)",
                      }}
                    />
                  </div>
                  <SearchBar onSearch={handleSearch} />
                </div>
              </div>

              {isLoading ? (
                <div className="w-full max-w-6xl mx-auto text-center text-gray-600">
                  Loading...
                </div>
              ) : hasRecentChats ? (
                <div className="w-full max-w-6xl mx-auto">
                  <h2 className="text-2xl font-semibold text-gray-900 text-center mb-8">
                    Your Recent Conversations
                  </h2>
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl shadow-sm border border-gray-200/50 overflow-hidden">
                    <RecentChats />
                  </div>
                </div>
              ) : (
                <HowItWorks />
              )}
            </div>
          </Container>
        </div>
      </main>
    </div>
  );
}
