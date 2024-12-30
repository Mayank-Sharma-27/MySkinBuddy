"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { getCookieId } from "../utils/cookies";
import { ChatMessage } from "./ChatMessage";
import dynamic from "next/dynamic";

const LoginModal = dynamic(() => import("./LoginModal"), {
  ssr: false,
});

interface Message {
  content: string;
  isBot: boolean;
  sources?: Array<{
    title: string;
    url: string;
  }>;
}

interface ProductInfo {
  imageUrl: string;
  productName: string;
  brandName: string;
}

export function ChatWindow({
  productId,
  fullPage = false,
  onClose,
}: {
  productId: string;
  fullPage?: boolean;
  onClose?: () => void;
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [productInfo, setProductInfo] = useState<ProductInfo>({
    imageUrl: "",
    productName: "",
    brandName: "",
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    const loadInitialChat = async () => {
      try {
        const cookieId = getCookieId();
        if (!cookieId) {
          console.error("No cookie ID available");
          return;
        }

        const response = await fetch("http://localhost:8080/start-chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Cookie-ID": cookieId,
          },
          body: JSON.stringify({
            product_id: productId,
          }),
        });

        if (!response.ok) {
          throw new Error("Failed to initialize chat");
        }

        const data = await response.json();

        if (data.status === "success" && data.chat_data) {
          const chatData = data.chat_data;

          // Set product info
          setProductInfo({
            imageUrl: chatData.image_url || "/placeholder-product.png",
            productName: chatData.product_name,
            brandName: chatData.brand_name,
          });

          // Set initial messages from chat history if any exists
          const initialMessages: Message[] =
            chatData.chat_history?.map((msg: any) => ({
              content: msg.content,
              isBot: msg.role === "assistant",
              sources: msg.sources || [],
            })) || [];

          // If no chat history, add the welcome message
          if (initialMessages.length === 0) {
            initialMessages.push({
              content: `👋 Hello! I'm ${chatData.brand_name}'s ${chatData.product_name}! You can ask me anything and I will try to help you!`,
              isBot: true,
              sources: [],
            });
          }

          setMessages(initialMessages);
        }
      } catch (error) {
        console.error("Error initializing chat:", error);
      }
    };

    if (productId) {
      loadInitialChat();
    }
  }, [productId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const cookieId = getCookieId();
    if (!cookieId) {
      console.error("No cookie ID available");
      return;
    }

    try {
      setIsLoading(true);
      const newUserMessage = { content: inputMessage.trim(), isBot: false };
      setMessages((prev) => [...prev, newUserMessage]);
      setInputMessage("");

      const response = await fetch("http://localhost:8080/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Cookie-ID": cookieId,
        },
        body: JSON.stringify({
          message: inputMessage.trim(),
          product_id: productId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No reader available");

      let accumulatedContent = "";
      let sources: Array<{ title: string; url: string }> = [];

      // Create a new bot message
      const botMessage = { content: "", isBot: true, sources: [] };
      setMessages((prev) => [...prev, botMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split("\n").filter((line) => line.trim());

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(5));
              if (data.content) {
                accumulatedContent += data.content;
                setMessages((prev) => {
                  const newMessages = [...prev];
                  const lastMessage = newMessages[newMessages.length - 1];
                  lastMessage.content = accumulatedContent;
                  lastMessage.sources = sources;
                  return newMessages;
                });
              }
              if (data.sources) {
                sources = data.sources;
              }
            } catch (e) {
              console.error("Error parsing chunk:", e);
            }
          }
        }
      }
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        {
          content: "Sorry, I encountered an error. Please try again.",
          isBot: true,
          sources: [],
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div
      className={
        fullPage
          ? "h-full"
          : "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4"
      }
    >
      <div
        className={
          fullPage
            ? "bg-white w-full h-full flex flex-col"
            : "bg-white rounded-lg w-full max-w-2xl h-[600px] flex flex-col"
        }
      >
        {/* Header */}
        <div className="p-4 border-b flex items-center justify-between bg-[#faf4f4]">
          <div className="flex items-center space-x-3">
            <div className="relative w-12 h-12 rounded-lg overflow-hidden">
              <Image
                src={productInfo.imageUrl}
                alt={productInfo.productName}
                fill
                className="object-cover"
                sizes="48px"
                priority
              />
            </div>
            <div>
              <h3 className="font-semibold text-[#a984b2]">
                {productInfo.productName}
              </h3>
              <p className="text-sm text-gray-600">{productInfo.brandName}</p>
            </div>
          </div>
          {!fullPage && onClose && (
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ×
            </button>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <ChatMessage
              key={index}
              message={message.content}
              isUser={!message.isBot}
              sources={message.sources}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="p-4 border-t">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask about this product..."
              className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#a984b2]"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !inputMessage.trim()}
              className={`px-4 py-2 rounded-lg ${
                isLoading || !inputMessage.trim()
                  ? "bg-gray-300 cursor-not-allowed"
                  : "bg-[#a984b2] hover:bg-[#8e6d97] text-white"
              }`}
            >
              {isLoading ? "..." : "Send"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
