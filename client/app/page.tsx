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
import Image from "next/image";

interface Product {
  product_id: string;
  product: string;
  brand: string;
  image_url: string;
  ingredients: string[] | null | undefined;
  match_score?: number;
  matching_features?: string[];
  subtitle?: string;
}

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default function Home() {
  const router = useRouter();
  const cookieId = useCookie();
  const [hasRecentChats, setHasRecentChats] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [searchResults, setSearchResults] = useState<Product[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [currentSearch, setCurrentSearch] = useState("");
  const LIMIT = 20;

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

  const handleSearch = async (
    productName: string,
    brandName: string,
    isLoadMore = false
  ) => {
    if (!isLoadMore) {
      setSearchResults([]);
      setOffset(0);
      setHasMore(true);
      setCurrentSearch(productName);
    }

    setIsSearching(true);
    try {
      const params = new URLSearchParams();
      if (productName) params.append("product", productName);
      if (brandName) params.append("brand", brandName);
      params.append("offset", isLoadMore ? offset.toString() : "0");
      params.append("limit", LIMIT.toString());

      const response = await fetch(
        `${API_URL}/search-products?${params.toString()}`,
        {
          headers: {
            "X-Cookie-ID": cookieId || "",
          },
        }
      );

      if (!response.ok) throw new Error("Search failed");
      const data = await response.json();

      if (data.length < LIMIT) {
        setHasMore(false);
      }

      setSearchResults((prev) => (isLoadMore ? [...prev, ...data] : data));
      if (isLoadMore) {
        setOffset((prev) => prev + LIMIT);
      }
    } catch (error) {
      console.error("Search error:", error);
      if (!isLoadMore) {
        setSearchResults([]);
      }
    } finally {
      setIsSearching(false);
    }
  };

  const loadMore = () => {
    if (!isSearching && hasMore && currentSearch) {
      handleSearch(currentSearch, "", true);
    }
  };

  // Add scroll handler to search results container
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const target = e.target as HTMLDivElement;
    if (
      target.scrollHeight - target.scrollTop === target.clientHeight &&
      hasMore &&
      !isSearching
    ) {
      loadMore();
    }
  };

  const handleProductSelect = (productId: string) => {
    router.push(`/chat/${productId}`);
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
                  Your personal skincare assistant to help you understand
                  products better for your skin.
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

                {/* Search Results */}
                {(isSearching || searchResults.length > 0) && (
                  <div
                    className="w-full max-w-3xl mx-auto mt-8 max-h-[600px] overflow-y-auto"
                    onScroll={handleScroll}
                  >
                    <div className="space-y-4">
                      {isSearching ? (
                        <div className="flex flex-col items-center justify-center p-8 bg-white/60 backdrop-blur-sm rounded-2xl">
                          <div className="relative w-16 h-16 mb-4">
                            <div className="absolute inset-0 rounded-full border-4 border-primary-100 opacity-25"></div>
                            <div className="absolute inset-0 rounded-full border-4 border-primary-500 border-t-transparent animate-spin"></div>
                          </div>
                          <div className="flex flex-col items-center gap-2">
                            <h3 className="text-lg font-medium text-primary-900">
                              Searching for your perfect match...
                            </h3>
                            <p className="text-sm text-primary-600">
                              Finding the best skincare products for you
                            </p>
                          </div>
                          <div className="mt-8 flex flex-col gap-4 w-full max-w-md">
                            {[...Array(3)].map((_, i) => (
                              <div
                                key={i}
                                className="flex items-center gap-4 p-4 bg-white rounded-xl"
                              >
                                <div className="w-16 h-16 rounded-lg bg-primary-50 animate-pulse"></div>
                                <div className="flex-1 space-y-2">
                                  <div className="h-4 bg-primary-50 rounded animate-pulse w-1/4"></div>
                                  <div className="h-4 bg-primary-50 rounded animate-pulse w-3/4"></div>
                                  <div className="flex gap-2">
                                    <div className="h-3 bg-primary-50 rounded-full animate-pulse w-16"></div>
                                    <div className="h-3 bg-primary-50 rounded-full animate-pulse w-16"></div>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        searchResults.map((product) => (
                          <div
                            key={product.product_id}
                            onClick={() =>
                              handleProductSelect(product.product_id)
                            }
                            className="flex flex-col sm:flex-row gap-4 sm:gap-6 bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer relative"
                          >
                            <div className="mx-auto sm:mx-0 w-56 h-56 sm:w-40 sm:h-40 relative">
                              <Image
                                src={product.image_url}
                                alt={product.product}
                                fill
                                className="rounded-lg object-contain"
                                sizes="(max-width: 640px) 224px, 160px"
                              />
                            </div>
                            <div className="flex-1 flex items-center">
                              <div className="w-full text-center sm:text-left">
                                <div className="text-base text-gray-600 font-medium">
                                  {product.brand}
                                </div>
                                <h3 className="text-lg font-semibold text-[#9333EA] mt-1">
                                  {product.product}
                                </h3>
                              </div>
                            </div>
                          </div>
                        ))
                      )}

                      {isSearching && searchResults.length > 0 && (
                        <div className="p-4 text-center">
                          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-primary-500 border-t-transparent"></div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {!searchResults.length &&
                (isLoading ? (
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
                ))}
            </div>
          </Container>
        </div>
      </main>
    </div>
  );
}
