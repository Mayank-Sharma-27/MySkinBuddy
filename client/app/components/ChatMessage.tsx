"use client";

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp: string;
}

export function ChatMessage({ message, isUser, timestamp }: ChatMessageProps) {
  const formatMessage = (text: string) => {
    // Split the text by ** markers
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, index) => {
      // Check if this part is wrapped in **
      if (part.startsWith("**") && part.endsWith("**")) {
        // Remove the ** and apply highlighting
        const ingredient = part.slice(2, -2);
        return (
          <span
            key={index}
            className="font-medium bg-primary-100/20 text-primary-700 px-1 rounded"
          >
            {ingredient}
          </span>
        );
      }
      return part;
    });
  };

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-gradient-to-r from-primary-500 to-secondary-500 text-white"
            : "bg-white border border-gray-200 text-gray-800"
        }`}
      >
        <p className="whitespace-pre-wrap break-words">
          {formatMessage(message)}
        </p>
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
