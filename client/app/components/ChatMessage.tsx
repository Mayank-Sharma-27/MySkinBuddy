"use client";

import { ChatMessage as ChatMessageType } from "../types";

interface ChatMessageProps {
  message: string | React.ReactNode;
  isUser: boolean;
  timestamp: string;
  isLoading?: boolean;
}

interface Source {
  name: string;
  url?: string;
}

function LoadingDots() {
  return (
    <div className="flex items-center space-x-1 px-2">
      <div
        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
        style={{ animationDelay: "0ms" }}
      ></div>
      <div
        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
        style={{ animationDelay: "150ms" }}
      ></div>
      <div
        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
        style={{ animationDelay: "300ms" }}
      ></div>
    </div>
  );
}

export function ChatMessage({
  message,
  isUser,
  timestamp,
  isLoading,
}: ChatMessageProps) {
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg p-4 ${
          isUser ? "bg-primary-600 text-white" : "bg-gray-100 dark:bg-gray-800"
        }`}
      >
        {typeof message === "string" ? (
          <div className="whitespace-pre-wrap">{message}</div>
        ) : (
          message
        )}
        <div className="text-xs mt-2 opacity-70">
          {new Date(timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}
