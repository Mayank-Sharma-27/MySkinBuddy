"use client";

import { useEffect, useRef, useState } from "react";
import { ChatMessage } from "./ChatMessage";
import { Button } from "./ui/Button";
import { useCookie } from "../utils/CookieProvider";
import { useAuth } from "../contexts/AuthContext";
import { API_URL } from "../config";
import dynamic from "next/dynamic";
import { SmartLoadingIndicator } from "./SmartLoadingIndicator";
import { flushSync } from "react-dom";

const LoginModal = dynamic(() => import("./LoginModal"), { ssr: false });

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: string;
  isLoading?: boolean;
  isThinkSection?: boolean;
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

const removeThinkSections = (content: string): string => {
  return content
    .replace(/<think>[\s\S]*?<\/think>/g, "")
    .replace(/\[\d+\]/g, "")
    .trim();
};

const removeCitationNumbers = (content: string): string => {
  return content.replace(/\[\d+\]/g, "");
};

const isInThinkSection = (content: string): boolean => {
  return content.includes("<think>") && !content.includes("</think>");
};

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
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  useEffect(() => {
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

      setIsInitialLoad(false);
    }
  }, [initialChatData]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  useEffect(() => {
  }, [initialChatData, messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !cookieId || isLoading) return;

    const messageContent = inputMessage.trim();
    setInputMessage("");
    setIsLoading(true);

    const userMessage: Message = {
      id: Date.now().toString(),
      content: messageContent,
      isUser: true,
      timestamp: new Date().toISOString(),
    };

    const assistantMessageId = (Date.now() + 1).toString();
    setMessages((prev) => [
      ...prev,
      userMessage,
      {
        id: assistantMessageId,
        content: "",
        isUser: false,
        timestamp: new Date().toISOString(),
        isLoading: true,
      },
    ]);

    try {
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
      if (!reader) throw new Error("No reader available");

      let accumulatedContent = "";
      let accumulatedCitations = "";
      let fullResponseReceived = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          fullResponseReceived = true;
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (!line.trim() || !line.startsWith("data: ")) continue;

          try {
            const jsonStr = line.replace("data: ", "").trim();
            const messageData = JSON.parse(jsonStr);

            if (messageData.type === "assistant_chunk") {
              let cleanContent = messageData.content;
              accumulatedContent += accumulatedContent
                ? cleanContent
                : ` ${cleanContent}`;

              flushSync(() => {
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? {
                          ...msg,
                          content: removeCitationNumbers(
                            accumulatedContent + accumulatedCitations
                          ),
                          isLoading: false,
                          isThinkSection: isInThinkSection(accumulatedContent),
                        }
                      : msg
                  )
                );
              });
            } else if (messageData.type === "citations") {
              accumulatedCitations += messageData.content;
              flushSync(() => {
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? {
                          ...msg,
                          content: removeCitationNumbers(
                            accumulatedContent + accumulatedCitations
                          ),
                          isLoading: false,
                        }
                      : msg
                  )
                );
              });
            }
          } catch (e) {
            console.error("Error parsing JSON:", e);
          }
        }
      }

      if (fullResponseReceived) {
        accumulatedContent = removeThinkSections(accumulatedContent);
      }

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content: removeCitationNumbers(
                  accumulatedContent + accumulatedCitations
                ),
                isLoading: false,
              }
            : msg
        )
      );
    } catch (error) {
      console.error("Error sending message:", error);
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
      {initialChatData.image_url && (isInitialLoad || messages.length <= 1) && (
        <div className="flex justify-center p-4 max-h-[300px] overflow-hidden bg-white border-b">
          <img
            src={initialChatData.image_url}
            alt={initialChatData.product_name}
            className="object-contain h-[250px] w-auto rounded-lg shadow-md"
            onError={(e) => {
              console.error("Image failed to load:", initialChatData.image_url);
              e.currentTarget.style.display = "none";
            }}
          />
        </div>
      )}
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
            isThinkSection={message.isThinkSection}
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
    </div>
  );
}
