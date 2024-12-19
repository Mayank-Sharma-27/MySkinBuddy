'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { getCookieId } from "../utils/cookies";

interface RecentChat {
  chat_id: string;
  product: string;
  brand: string;
  image_url: string;
}

export default function RecentChats() {
  const [recentChats, setRecentChats] = useState<RecentChat[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchRecentChats = async () => {
      try {
        const response = await fetch('http://localhost:8080/recent-chats', {
          headers: {
            'X-Cookie-ID': getCookieId(),
          },
        });
        const data = await response.json();
        if (data.status === 'success') {
          setRecentChats(data.chats);
        }
      } catch (error) {
        console.error('Error fetching recent chats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRecentChats();
  }, []);

  const handleChatSelect = async (chat: RecentChat) => {
    try {
      const cookieId = getCookieId();
      if (!cookieId) {
        throw new Error('No cookie ID available');
      }

      const response = await fetch('http://localhost:8080/start-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Cookie-ID': cookieId,
        },
        body: JSON.stringify({
          product_id: chat.product_id,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to start chat');
      }

      const data = await response.json();
      if (data.status === 'success') {
        router.push(`/chat/${chat.product_id}?chat_id=${data.chat_id}`);
      } else {
        throw new Error(data.error || 'Failed to start chat');
      }
    } catch (error) {
      console.error('Error starting chat:', error);
    }
  };

  if (loading) {
    return (
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-4 overflow-x-auto pb-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="animate-pulse flex-shrink-0 w-[200px] h-[120px] bg-gray-100 rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (recentChats.length === 0) {
    return null;
  }

  return (
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <h2 className="text-[#a984b2] text-2xl font-medium mb-6">Recent Chats</h2>
      <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
        {recentChats.map((chat) => (
          <div
            key={chat.chat_id}
            onClick={() => handleChatSelect(chat)}
            className="cursor-pointer flex-shrink-0 group"
          >
            <div className="w-[200px] bg-white rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow duration-200">
              <div className="relative h-[120px] w-full">
                <Image
                  src={chat.image_url || '/placeholder-product.png'}
                  alt={chat.product}
                  fill
                  className="object-cover"
                  sizes="200px"
                />
              </div>
              <div className="p-3">
                <h3 className="text-gray-800 font-medium truncate text-sm">
                  {chat.product}
                </h3>
                <p className="text-gray-500 text-xs truncate mt-1">
                  {chat.brand}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 