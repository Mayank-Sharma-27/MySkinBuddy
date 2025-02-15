"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useCookie } from "../utils/CookieProvider";
import { API_URL } from "../config";
import Image from "next/image";
import { useMessageLimit } from "../contexts/MessageLimitContext";

interface Chat {
  image_url: string;
  product: string;
  product_id: string;
  product_name: string;
  brand_name: string;
}

export default function RecentChats() {
  const router = useRouter();
  const cookieId = useCookie();
  const { checkMessageLimit } = useMessageLimit();
  const [chats, setChats] = useState<Chat[]>([]);
  const [displayedChats, setDisplayedChats] = useState<Chat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const CHATS_PER_PAGE = 5;

  useEffect(() => {
    const fetchChats = async () => {
      try {
        if (!cookieId) {
          setError("Session error. Please refresh the page.");
          return;
        }

        const response = await fetch(`${API_URL}/all-chats`, {
          headers: {
            "X-Cookie-ID": cookieId,
          },
        });

        const data = await response.json();
        if (data.status === "success") {
          setChats(data.chats);
          setDisplayedChats(data.chats.slice(0, CHATS_PER_PAGE));
        } else {
          setError(data.error || "Failed to load chats");
        }
      } catch (error) {
        console.error("Error fetching chats:", error);
        setError("Failed to load chats. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchChats();
  }, [cookieId]);

  const loadMoreChats = () => {
    const currentLength = displayedChats.length;
    const nextChats = chats.slice(
      currentLength,
      currentLength + CHATS_PER_PAGE
    );
    setDisplayedChats([...displayedChats, ...nextChats]);
  };

  const handleChatSelect = async (chat: Chat) => {
    try {
      const canProceed = await checkMessageLimit();
      if (!canProceed) return;

      router.push(`/chat/${chat.product_id}`);
    } catch (error) {
      setError("Failed to open chat. Please try again.");
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-center text-gray-500">
        <div className="animate-pulse flex flex-col gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex gap-6 p-6 bg-white/60 rounded-xl">
              <div className="w-24 h-24 bg-gray-200 rounded-xl"></div>
              <div className="flex-1 space-y-3 py-2">
                <div className="h-5 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center">
        <div className="text-red-500 mb-4">{error}</div>
        <button
          onClick={() => window.location.reload()}
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (chats.length === 0) {
    return (
      <div className="p-12 text-center">
        <div className="text-gray-500 mb-6">
          No conversations yet. Start by searching for a product!
        </div>
        <button
          onClick={() => router.push("/")}
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          Search Products
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {displayedChats.map((chat) => (
          <button
            key={chat.product_id}
            onClick={() => handleChatSelect(chat)}
            className="flex gap-6 p-6 rounded-xl bg-white/60 backdrop-blur-sm hover:bg-white/80 
                       transition-all duration-200 group border border-gray-100 
                       hover:border-primary-100 hover:shadow-lg hover:-translate-y-0.5"
          >
            <div className="relative w-24 h-24 flex-shrink-0">
              <Image
                src={chat.image_url}
                alt={chat.product_name}
                fill
                className="object-cover rounded-xl"
                sizes="(max-width: 768px) 96px, 96px"
              />
            </div>
            <div className="flex-1 text-left py-2">
              <h3
                className="text-lg font-medium text-gray-900 group-hover:text-primary-600 
                           transition-colors line-clamp-2 mb-2"
              >
                {chat.product_name}
              </h3>
              <p className="text-sm text-gray-500 capitalize flex items-center">
                <span className="inline-block">By {chat.brand_name}</span>
              </p>
            </div>
          </button>
        ))}
      </div>

      {displayedChats.length < chats.length && (
        <div className="flex justify-center mt-4">
          <button
            onClick={loadMoreChats}
            className="px-6 py-2 text-primary-600 hover:text-primary-700 
                     border border-primary-200 rounded-lg hover:bg-primary-50
                     transition-colors duration-200"
          >
            Load More
          </button>
        </div>
      )}
    </div>
  );
}
