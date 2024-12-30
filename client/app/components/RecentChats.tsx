"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useCookie } from "../utils/CookieProvider";

interface Chat {
  id: string;
  product_name: string;
  last_message: string;
  timestamp: string;
}

export default function RecentChats() {
  const router = useRouter();
  const cookieId = useCookie();
  const [chats, setChats] = useState<Chat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchChats = async () => {
      try {
        if (!cookieId) {
          setError("Session error. Please refresh the page.");
          return;
        }

        const response = await fetch("http://localhost:8080/chats/recent", {
          headers: {
            "X-Cookie-ID": cookieId,
          },
        });

        const data = await response.json();
        if (data.status === "success") {
          setChats(data.chats);
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

  if (loading) {
    return (
      <div className="p-8 text-center text-gray-500">
        Loading recent conversations...
      </div>
    );
  }

  if (error) {
    return <div className="p-8 text-center text-red-500">{error}</div>;
  }

  if (chats.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        No conversations yet. Start by searching for a product!
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-200/50">
      {chats.map((chat) => (
        <button
          key={chat.id}
          onClick={() => router.push(`/chat/${chat.id}`)}
          className="w-full p-6 text-left hover:bg-white/40 transition-colors group"
        >
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
              {chat.product_name}
            </h3>
            <span className="text-sm text-gray-500">
              {new Date(chat.timestamp).toLocaleDateString()}
            </span>
          </div>
          <p className="text-gray-600 line-clamp-2">{chat.last_message}</p>
        </button>
      ))}
    </div>
  );
}
