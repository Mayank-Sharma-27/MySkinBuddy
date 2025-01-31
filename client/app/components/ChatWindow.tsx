"use client";

import { useEffect, useRef, useState } from "react";
import { ChatMessage } from "./ChatMessage";
import { Button } from "./ui/Button";
import { useCookie } from "../utils/CookieProvider";
import { useAuth } from "../contexts/AuthContext";
import dynamic from "next/dynamic";
import { API_URL } from "../config";

const LoginModal = dynamic(() => import("./LoginModal"), { ssr: false });

function LoadingDots() {
  return (
    <div className="flex items-center h-4">
      <div className="flex space-x-1">
        <div className="loading-dot"></div>
        <div className="loading-dot"></div>
        <div className="loading-dot"></div>
      </div>
    </div>
  );
}

interface Message {
  id: string;
  content: string;
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
  preloaded_context: any;
}

interface ChatWindowProps {
  productId: string;
  chatData: ChatData;
  fullPage?: boolean;
}

export function ChatWindow({
  productId,
  chatData,
  fullPage = false,
}: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [currentPage, setCurrentPage] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const cookieId = useCookie();
  const { isLoggedIn } = useAuth();

  const loadMoreMessages = async () => {
    if (isLoadingMore || !hasMore || !cookieId) return;

    try {
      setIsLoadingMore(true);
      const response = await fetch(
        `${API_URL}/chat/${productId}/history?page=${currentPage + 1}`,
        {
          headers: {
            "X-Cookie-ID": cookieId,
          },
        }
      );

      if (!response.ok) throw new Error("Failed to load more messages");

      const data = await response.json();
      if (data.status === "success") {
        const oldMessages = data.chat_data.chat_history.map((msg: any) => ({
          id: msg.id || Date.now().toString(),
          content: msg.content,
          isUser: msg.role === "user",
          timestamp: msg.timestamp || new Date().toISOString(),
        }));

        setMessages((prev) => [...oldMessages, ...prev]);
        setCurrentPage((prev) => prev + 1);
        setHasMore(data.chat_data.pagination.has_more);
      }
    } catch (error) {
      console.error("Error loading more messages:", error);
    } finally {
      setIsLoadingMore(false);
    }
  };

  const handleScroll = () => {
    if (!messagesContainerRef.current) return;

    const { scrollTop } = messagesContainerRef.current;
    if (scrollTop === 0 && hasMore) {
      loadMoreMessages();
    }
  };

  useEffect(() => {
    // Initialize messages from chat data
    if (chatData) {
      const welcomeMessage = {
        id: "welcome",
        content: `Hi! I am ${chatData.product_name} from ${chatData.brand_name}. Please let me help you.`,
        isUser: false,
        timestamp: new Date().toISOString(),
      };

      const formattedMessages = chatData.chat_history.map((msg: any) => ({
        id: msg.id || Date.now().toString(),
        content: msg.content,
        isUser: msg.role === "user",
        timestamp: msg.timestamp || new Date().toISOString(),
      }));

      setMessages(
        formattedMessages.length > 0 ? formattedMessages : [welcomeMessage]
      );
      setCurrentPage(formattedMessages.length);
    }
  }, [chatData]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !cookieId) return;

    const newMessage = {
      id: Date.now().toString(),
      content: inputMessage,
      isUser: true,
      timestamp: new Date().toISOString(),
    };

    // Add loading message
    const loadingMessage = {
      id: "loading-" + Date.now().toString(),
      content: "",
      isUser: false,
      timestamp: new Date().toISOString(),
      isLoading: true,
    };

    setMessages((prev) => [...prev, newMessage, loadingMessage]);
    setInputMessage("");
    setIsLoading(true);

    // Scroll to bottom immediately when sending
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Cookie-ID": cookieId,
        },
        body: JSON.stringify({
          product_id: productId,
          message: inputMessage,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        if (response.status === 403 && errorData.requires_login) {
          setShowLoginModal(true);
          return;
        }
        throw new Error("Failed to send message");
      }

      const reader = response.body?.getReader();
      let partialResponse = "";

      // Remove loading message when we start getting real response
      setMessages((prev) => prev.filter((msg) => !msg.isLoading));

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = new TextDecoder().decode(value);
          const lines = (partialResponse + chunk).split("\n");
          partialResponse = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.content) {
                  setMessages((prev) => {
                    const lastMessage = prev[prev.length - 1];
                    if (!lastMessage.isUser && !lastMessage.isLoading) {
                      // Update existing assistant message
                      return [
                        ...prev.slice(0, -1),
                        {
                          ...lastMessage,
                          content: lastMessage.content + data.content,
                        },
                      ];
                    } else {
                      // Create new assistant message
                      return [
                        ...prev,
                        {
                          id: Date.now().toString(),
                          content: data.content,
                          isUser: false,
                          timestamp: new Date().toISOString(),
                        },
                      ];
                    }
                  });
                }
              } catch (e) {
                console.error("Error parsing SSE data:", e);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error("Error sending message:", error);
      // Remove loading message and show error
      setMessages((prev) => [
        ...prev.filter((msg) => !msg.isLoading),
        {
          id: Date.now().toString(),
          content:
            "Sorry, there was an error sending your message. Please try again.",
          isUser: false,
          timestamp: new Date().toISOString(),
        },
      ]);
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
      <div
        ref={messagesContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto p-4 bg-gray-50"
      >
        {isLoadingMore && (
          <div className="text-center py-2">
            <ChatMessage
              message=""
              isUser={false}
              timestamp={new Date().toISOString()}
              isLoading={true}
            />
          </div>
        )}
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message.content}
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
