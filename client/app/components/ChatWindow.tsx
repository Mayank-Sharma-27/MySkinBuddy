"use client";
import { useState, useRef, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
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

interface StreamResponse {
  content: string;
  sources: Array<{
    title: string;
    url: string;
  }>;
}

interface StreamChunk {
  content: string;
  sources: Array<{ url: string; title: string }>;
  type?: "final";
}

export function ChatWindow({
  chatId,
  productId,
  fullPage = false,
  onClose,
  existing = false,
}: {
  chatId: string;
  productId: string;
  fullPage?: boolean;
  onClose?: () => void;
  existing?: boolean;
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [initialMessage, setInitialMessage] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [productName, setProductName] = useState("");
  const [brandName, setBrandName] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const searchParams = useSearchParams();

  // Load chat history for existing chats
  useEffect(() => {
    const loadChatHistory = async () => {
      if (!existing) return;

      try {
        const response = await fetch(
          `http://localhost:8080/chat/${chatId}/history`,
          {
            headers: {
              "X-Cookie-ID": getCookieId(),
            },
          }
        );

        if (!response.ok) throw new Error("Failed to load chat history");

        const data = await response.json();

        // Transform chat history into messages format
        const chatHistory = data.chat_history.map((msg: any) => ({
          content: msg.content,
          isBot: msg.role === "assistant",
          sources: msg.sources || [],
        }));

        setMessages(chatHistory);
      } catch (error) {
        console.error("Error loading chat history:", error);
      }
    };

    loadChatHistory();
  }, [chatId, existing]);

  // Load initial message and chat data for new chats
  useEffect(() => {
    const loadInitialChat = async () => {
      if (existing) return; // Skip for existing chats

      try {
        const response = await fetch("http://localhost:8080/start-chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Cookie-ID": getCookieId(),
          },
          body: JSON.stringify({
            product_id: productId,
          }),
        });

        if (!response.ok) throw new Error("Failed to initialize chat");

        const data = await response.json();
        const chatData = data.chat_data;

        // Store chat data in localStorage
        localStorage.setItem(`chat_data_${chatId}`, JSON.stringify(chatData));

        // Set the initial message and other data
        setInitialMessage(chatData.initial_message);
        setImageUrl(chatData.image_url);
        setProductName(chatData.product_name);
        setBrandName(chatData.brand_name);

        // Add initial message to messages array
        setMessages([
          {
            content: chatData.initial_message,
            isBot: true,
            sources: [],
          },
        ]);
      } catch (error) {
        console.error("Error initializing chat:", error);
      }
    };

    loadInitialChat();
  }, [chatId, productId, existing]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    try {
      setIsLoading(true);
      const newUserMessage = { content: inputMessage.trim(), isBot: false };
      setMessages((prev) => [...prev, newUserMessage]);
      setInputMessage("");

      const response = await fetch('http://localhost:8080/chat', {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Cookie-ID": getCookieId(),
        },
        body: JSON.stringify({ 
          message: inputMessage.trim(),
          chat_id: chatId,
          product_id: productId  // Make sure productId is available in props or context
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No reader available");

      let accumulatedContent = "";
      let sources: string[] = [];

      // Create a new bot message
      const botMessage = { content: "", isBot: true, sources: [] };
      setMessages((prev) => [...prev, botMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Convert the chunk to text
        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split("\n").filter((line) => line.trim());

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(5));
              if (data.content) {
                // If this is the last message containing sources
                if (data.content.includes("http")) {
                  sources = data.content.split(", ");
                } else {
                  accumulatedContent += data.content;
                  // Update the last message's content
                  setMessages((prev) => {
                    const newMessages = [...prev];
                    const lastMessage = newMessages[newMessages.length - 1];
                    lastMessage.content = accumulatedContent;
                    lastMessage.sources = sources;
                    return newMessages;
                  });
                }
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

  // Auto-scroll effect
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const formatContent = (content: string) => {
    // Check if content is a comma-separated list of URLs
    if (content.includes("http") && content.includes(",")) {
      const links = content.split(",").map((url) => url.trim());
      return (
        <div className="flex flex-col gap-2">
          {links.map((url, index) => (
            <a
              key={index}
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 hover:text-blue-700 underline break-all"
            >
              {new URL(url).hostname}
            </a>
          ))}
        </div>
      );
    }

    // Regular content
    return <span>{content}</span>;
  };

  return (
    <>
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
              <div className="w-12 h-12 rounded-lg overflow-hidden">
                <img
                  src={imageUrl}
                  alt={productName}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.src = "/placeholder-product.png";
                  }}
                />
              </div>
              <div>
                <h3 className="font-semibold text-[#a984b2]">{productName}</h3>
                <p className="text-sm text-gray-600">{brandName}</p>
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

      {showLoginModal && (
        <LoginModal
          onClose={() => setShowLoginModal(false)}
          message="Continue the conversation by signing in or creating an account. This helps us provide a better experience."
        />
      )}
    </>
  );
}
