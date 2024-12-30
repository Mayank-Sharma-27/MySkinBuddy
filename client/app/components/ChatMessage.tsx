"use client";

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp: string;
}

export function ChatMessage({ message, isUser, timestamp }: ChatMessageProps) {
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-gradient-to-r from-primary-500 to-secondary-500 text-white"
            : "bg-white border border-gray-200 text-gray-800"
        }`}
      >
        <p className="whitespace-pre-wrap break-words">{message}</p>
        <div
          className={`text-xs mt-1 ${
            isUser ? "text-white/70" : "text-gray-500"
          }`}
        >
          {new Date(timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}
