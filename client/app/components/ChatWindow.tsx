"use client";

import { useEffect, useRef, useState } from "react";
import { ChatMessage } from "./ChatMessage";
import { Button } from "./ui/Button";
import { useCookie } from "../utils/CookieProvider";
import { useAuth } from "../contexts/AuthContext";
import { io, Socket } from "socket.io-client";
import { API_URL } from "../config";
import dynamic from "next/dynamic";

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
  chatData: initialChatData,
  fullPage = false,
}: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const socketRef = useRef<Socket>();
  const cookieId = useCookie();
  const { isLoggedIn } = useAuth();

  useEffect(() => {
    // Initialize socket connection
    socketRef.current = io(API_URL, {
      transports: ["websocket"],
      query: {
        cookie_id: cookieId,
      },
    });

    // Join chat room
    if (cookieId && productId) {
      socketRef.current.emit("join_chat", {
        cookie_id: cookieId,
        product_id: productId,
      });
    }

    // Handle socket connection events
    socketRef.current.on("connect", () => {
      // Socket connected
    });

    socketRef.current.on("connect_error", (error) => {
      // Handle connection error silently
    });

    // Handle incoming messages
    socketRef.current.on("message", (data: any) => {
      if (data.type === "user_message") {
        // We already added the user message locally, so skip
        return;
      } else if (data.type === "assistant_chunk") {
        setMessages((prev) => {
          const lastMessage = prev[prev.length - 1];
          if (!lastMessage?.isUser) {
            // Update existing assistant message
            const updatedMessages = [...prev];
            updatedMessages[prev.length - 1] = {
              ...lastMessage,
              content: (lastMessage?.content || "") + data.content,
              isLoading: true,
            };
            return updatedMessages;
          }
          return prev;
        });
      } else if (data.type === "done") {
        setMessages((prev) => {
          const lastMessage = prev[prev.length - 1];
          if (!lastMessage?.isUser) {
            const updatedMessages = [...prev];
            updatedMessages[prev.length - 1] = {
              ...lastMessage,
              isLoading: false,
            };
            return updatedMessages;
          }
          return prev;
        });
        setIsLoading(false);
      }
    });

    // Handle chat history
    socketRef.current.on("chat_history", (data: any) => {
      if (!data) return;

      const formattedMessages =
        data.chat_history?.map((msg: any) => ({
          id: msg.id || Date.now().toString(),
          content: msg.content,
          isUser: msg.role === "user",
          timestamp: msg.timestamp || new Date().toISOString(),
        })) || [];

      if (formattedMessages.length === 0 && data.product_name) {
        const welcomeMessage = {
          id: "welcome",
          content: `Hi! I am ${data.product_name} from ${data.brand_name}. Please let me help you.`,
          isUser: false,
          timestamp: new Date().toISOString(),
        };
        setMessages([welcomeMessage]);
      } else {
        setMessages(formattedMessages);
      }
    });

    // Handle errors
    socketRef.current.on("error", (error: any) => {
      if (error.requires_login) {
        setShowLoginModal(true);
      }
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.emit("leave_chat", {
          cookie_id: cookieId,
          product_id: productId,
        });
        socketRef.current.disconnect();
      }
    };
  }, [cookieId, productId]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !cookieId || isLoading) return;

    const messageContent = inputMessage.trim();

    // Add user message locally first
    const userMessage = {
      id: Date.now().toString(),
      content: messageContent,
      isUser: true,
      timestamp: new Date().toISOString(),
    };

    // Add an immediate loading message for the assistant
    const loadingMessage = {
      id: Date.now().toString() + "-loading",
      content: "",
      isUser: false,
      timestamp: new Date().toISOString(),
      isLoading: true,
    };

    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    setInputMessage("");
    setIsLoading(true);

    // Emit the message
    socketRef.current?.emit("chat_message", {
      cookie_id: cookieId,
      product_id: productId,
      message: messageContent,
    });
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
