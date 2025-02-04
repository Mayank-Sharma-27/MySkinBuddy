"use client";

import { useEffect, useState } from "react";
import { ChatWindow } from "../../components/ChatWindow";
import Navbar from "../../components/Navbar";
import { API_URL } from "../../config";
import { useCookie } from "../../utils/CookieProvider";

interface ChatData {
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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const cookieId = useCookie();
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    let mounted = true;

    const initializeChat = async () => {
      try {
        // Wait for cookie to be available
        if (!cookieId) {
          if (retryCount < 3) {
            // Retry after a short delay
            setTimeout(() => {
              if (mounted) {
                setRetryCount((prev) => prev + 1);
              }
            }, 1000);
            return;
          }
          setError("Unable to initialize session. Please refresh the page.");
          setLoading(false);
          return;
        }

        try {
          // First try to get existing chat
          const historyResponse = await fetch(
            `${API_URL}/chat/${product_id}/history?page=0`,
            {
              headers: {
                "X-Cookie-ID": cookieId,
              },
            }
          );

          if (!mounted) return;

          // Even if history fetch fails, we'll continue with empty chat data
          const historyData = historyResponse.ok
            ? await historyResponse.json()
            : {
                status: "success",
                chat_data: {
                  product_id,
                  product_name: "",
                  brand_name: "",
                  image_url: "",
                  chat_history: [],
                },
              };

          if (!mounted) return;

          // Initialize new chat if we don't have product info
          if (
            historyData.status === "success" &&
            historyData.chat_data &&
            (!historyData.chat_data.product_name ||
              !historyData.chat_data.brand_name)
          ) {
            try {
              // Initialize new chat
              const startChatResponse = await fetch(`${API_URL}/start-chat`, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                  "X-Cookie-ID": cookieId,
                },
                body: JSON.stringify({
                  product_id: product_id,
                }),
              });

              if (!mounted) return;

              if (startChatResponse.ok) {
                const data = await startChatResponse.json();
                if (data.status === "success" && data.chat_data) {
                  setChatData(data.chat_data);
                } else {
                  // If start chat fails, use empty chat data
                  setChatData({
                    product_id,
                    chat_history: [],
                    product_name: "",
                    brand_name: "",
                    image_url: "",
                    preloaded_context: null,
                  });
                }
              } else {
                // If start chat fails, use empty chat data
                setChatData({
                  product_id,
                  chat_history: [],
                  product_name: "",
                  brand_name: "",
                  image_url: "",
                  preloaded_context: null,
                });
              }
            } catch (error) {
              // If start chat fails, use empty chat data
              console.error("Error starting chat:", error);
              setChatData({
                product_id,
                chat_history: [],
                product_name: "",
                brand_name: "",
                image_url: "",
                preloaded_context: null,
              });
            }
          } else if (
            historyData.status === "success" &&
            historyData.chat_data
          ) {
            // Use existing chat data
            setChatData(historyData.chat_data);
          } else {
            // Use empty chat data as fallback
            setChatData({
              product_id,
              chat_history: [],
              product_name: "",
              brand_name: "",
              image_url: "",
              preloaded_context: null,
            });
          }
        } catch (error) {
          console.error("Error fetching chat history:", error);
          // Use empty chat data as fallback
          setChatData({
            product_id,
            chat_history: [],
            product_name: "",
            brand_name: "",
            image_url: "",
            preloaded_context: null,
          });
        }
      } catch (error) {
        console.error("Error in initializeChat:", error);
        // Use empty chat data as fallback
        setChatData({
          product_id,
          chat_history: [],
          product_name: "",
          brand_name: "",
          image_url: "",
          preloaded_context: null,
        });
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    initializeChat();

    return () => {
      mounted = false;
    };
  }, [product_id, cookieId, retryCount]);

  const handleRetry = () => {
    setLoading(true);
    setError(null);
    setRetryCount(0);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#faf4f4]">
        <Navbar />
        <div className="h-[calc(100vh-64px)] flex items-center justify-center">
          <div className="flex flex-col items-center space-y-4">
            <div className="dots-container">
              <div className="loading-dot"></div>
              <div className="loading-dot"></div>
              <div className="loading-dot"></div>
            </div>
            <div className="text-gray-500 mt-4">Loading chat...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#faf4f4]">
        <Navbar />
        <div className="h-[calc(100vh-64px)] flex items-center justify-center">
          <div className="text-center">
            <div className="text-red-500 mb-4">{error}</div>
            <button
              onClick={handleRetry}
              className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!chatData) {
    return (
      <div className="min-h-screen bg-[#faf4f4]">
        <Navbar />
        <div className="h-[calc(100vh-64px)] flex items-center justify-center">
          <div className="text-gray-500">No chat data available.</div>
        </div>
      </div>
    );
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
