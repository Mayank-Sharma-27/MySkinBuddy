"use client";

import { useEffect, useRef, useState } from "react";
import { ChatMessage } from "./ChatMessage";
import { Button } from "./ui/Button";
import { useCookie } from "../utils/CookieProvider";
import { useAuth } from "../contexts/AuthContext";
import { API_URL } from "../config";
import dynamic from "next/dynamic";
import { SmartLoadingIndicator } from "./SmartLoadingIndicator";

const LoginModal = dynamic(() => import("./LoginModal"), { ssr: false });

interface Message {
  id: string;
  content: string | React.ReactNode;
  isUser: boolean;
  timestamp: string;
  isLoading?: boolean;
}

interface ChatData {
  chat_history: any[];
  product_id: string;
  product_name: string;
  brand_name: string;
  image_url: string;
}

interface ChatWindowProps {
  productId: string;
  chatData: ChatData;
  fullPage?: boolean;
}

export function ChatWindow({
  productId,
  chatData: initialChatData,
  fullPage = false,
}: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const cookieId = useCookie();
  const { isLoggedIn } = useAuth();
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    // Initialize messages from chat data
    if (initialChatData?.chat_history) {
      const formattedMessages = initialChatData.chat_history.map(
        (msg: any) => ({
          id: msg.id || Date.now().toString(),
          content: msg.content,
          isUser: msg.role === "user",
          timestamp: msg.timestamp || new Date().toISOString(),
        })
      );
      setMessages(formattedMessages);
    }
  }, [initialChatData]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !cookieId || isLoading) return;

    const messageContent = inputMessage.trim();
    setInputMessage("");
    setIsLoading(true);

    // Add user message immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      content: messageContent,
      isUser: true,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      // Create loading message for assistant
      const loadingMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "",
        isUser: false,
        timestamp: new Date().toISOString(),
        isLoading: true,
      };
      setMessages((prev) => [...prev, loadingMessage]);

      // Send message to server
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Cookie-ID": cookieId,
        },
        body: JSON.stringify({
          product_id: productId,
          message: messageContent,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        if (error.requires_login) {
          setShowLoginModal(true);
        }
        throw new Error(error.message || "Failed to send message");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let accumulatedResponse = "";

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const rawData = line.slice(5);
                if (!rawData.trim()) continue;

                const data = JSON.parse(rawData);
                console.log("Received data:", data);

                if (data.type === "error") {
                  throw new Error(data.content);
                }

                // Handle different response formats
                let content = "";
                if (data.content) {
                  content = data.content;
                } else if (data.response_metadata) {
                  // Extract content from the LangChain format
                  content = data.text || data.content || "";
                } else if (typeof data === "string") {
                  content = data;
                }

                if (content) {
                  accumulatedResponse = content;
                  // Update the assistant message
                  setMessages((prev) => {
                    const newMessages = [...prev];
                    const lastMessage = newMessages[newMessages.length - 1];
                    if (!lastMessage.isUser) {
                      lastMessage.content = accumulatedResponse;
                      lastMessage.isLoading = true;
                    }
                    return newMessages;
                  });
                }
              } catch (e) {
                console.error("Error parsing SSE data:", e, "Raw line:", line);
              }
            }
          }
        }
      }

      // Final update to remove loading state
      setMessages((prev) => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (!lastMessage.isUser) {
          lastMessage.content = accumulatedResponse;
          lastMessage.isLoading = false;
        }
        return newMessages;
      });
    } catch (error) {
      console.error("Error sending message:", error);
      // Remove loading message on error
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className={`flex flex-col ${
        fullPage ? "h-[calc(100vh-4rem)]" : "h-[600px]"
      }`}
    >
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={
              message.isLoading ? <SmartLoadingIndicator /> : message.content
            }
            isUser={message.isUser}
            timestamp={message.timestamp}
            isLoading={message.isLoading || false}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form
        onSubmit={handleSendMessage}
        className="p-4 bg-white border-t border-gray-200"
      >
        <div className="flex gap-4">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask about the product..."
            className="flex-1 px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-colors"
            disabled={isLoading}
          />
          <Button type="submit" variant="gradient" disabled={isLoading}>
            {isLoading ? "Sending..." : "Send"}
          </Button>
        </div>
      </form>

      {showLoginModal && (
        <LoginModal
          message="Please login to continue chatting. You have reached the message limit for anonymous users."
          onClose={() => setShowLoginModal(false)}
        />
      )}
    </div>
  );
}
