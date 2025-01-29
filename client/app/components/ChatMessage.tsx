"use client";

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp: string;
  isLoading?: boolean;
}

function LoadingDots() {
  return (
    <div className="flex space-x-1.5 items-center h-6">
      <div className="w-2 h-2 rounded-full bg-primary-500 animate-bounce [animation-delay:-0.3s]"></div>
      <div className="w-2 h-2 rounded-full bg-primary-500 animate-bounce [animation-delay:-0.15s]"></div>
      <div className="w-2 h-2 rounded-full bg-primary-500 animate-bounce"></div>
    </div>
  );
}

export function ChatMessage({
  message,
  isUser,
  timestamp,
  isLoading = false,
}: ChatMessageProps) {
  const formatMessage = (text: string) => {
    // First split by markdown links [text](url)
    const parts = text.split(/(\[.*?\]\(.*?\))/g);

    return parts.map((part, index) => {
      // Check if this part is a markdown link
      const linkMatch = part.match(/\[(.*?)\]\((.*?)\)/);
      if (linkMatch) {
        const [_, text, url] = linkMatch;
        return (
          <a
            key={index}
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className={`underline ${
              isUser
                ? "text-white/90 hover:text-white"
                : "text-primary-600 hover:text-primary-700"
            }`}
          >
            {text}
          </a>
        );
      }

      // Handle bold text within non-link parts
      const boldParts = part.split(/(\*\*[^*]+\*\*)/g);
      return boldParts.map((boldPart, boldIndex) => {
        if (boldPart.startsWith("**") && boldPart.endsWith("**")) {
          const ingredient = boldPart.slice(2, -2);
          return (
            <span
              key={`${index}-${boldIndex}`}
              className="font-medium bg-primary-100/20 text-primary-700 px-1 rounded"
            >
              {ingredient}
            </span>
          );
        }
        return boldPart;
      });
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
        {isLoading ? (
          <div className="min-h-[24px] flex items-center">
            <LoadingDots />
          </div>
        ) : (
          <p className="whitespace-pre-wrap break-words">
            {formatMessage(message)}
          </p>
        )}
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
