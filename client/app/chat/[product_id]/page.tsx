"use client";

import { useEffect, useState } from "react";
import { ChatWindow } from "../../components/ChatWindow";
import Navbar from "../../components/Navbar";

interface ChatData {
  chat_id: string;
  chat_history: any[];
  product_id: string;
  product_name: string;
  brand_name: string;
  image_url: string;
  preloaded_context: any;
}

interface PageProps {
  params: {
    product_id: string;
  };
}

export default function ChatPage({ params }: PageProps) {
  const { product_id } = params;
  const [chatData, setChatData] = useState<ChatData | null>(null);

  useEffect(() => {
    const chatDataString = localStorage.getItem(`chat_data_${product_id}`);
    if (chatDataString) {
      try {
        const data = JSON.parse(chatDataString);
        setChatData(data);
      } catch (error) {
        console.error("Error parsing chat data:", error);
      }
    }
  }, [product_id]);

  if (!chatData) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-[#faf4f4]">
      <Navbar />
      <div className="h-[calc(100vh-64px)]">
        <ChatWindow
          productId={product_id}
          chatData={chatData}
          fullPage={true}
        />
      </div>
    </div>
  );
}
