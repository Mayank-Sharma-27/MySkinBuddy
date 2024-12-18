'use client';
import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  sources?: Array<{
    title: string;
    url: string;
  }>;
}

export function ChatMessage({ message, isUser, sources }: ChatMessageProps) {
  const [formattedMessage, setFormattedMessage] = useState(message);

  useEffect(() => {
    setFormattedMessage(message);
  }, [message]);

  const messageContainerClass = isUser ? 'justify-end' : 'justify-start';
  const messageBackgroundClass = isUser ? 'bg-[#a984b2] text-white' : 'bg-gray-100';

  return (
    <div className={`flex ${messageContainerClass} mb-4`}>
      <div className={`rounded-lg p-4 max-w-[80%] ${messageBackgroundClass}`}>
        {isUser ? (
          <p>{formattedMessage}</p>
        ) : (
          <div className="space-y-4">
            <ReactMarkdown
              components={{
                strong: ({ children }) => (
                  <span className="font-bold text-[#a984b2]">{children}</span>
                ),
                p: ({ children }) => (
                  <p className="mb-2">{children}</p>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc ml-4 mb-2">{children}</ul>
                ),
                li: ({ children }) => (
                  <li className="mb-1">{children}</li>
                ),
              }}
            >
              {formattedMessage}
            </ReactMarkdown>
            
            {sources && sources.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-sm font-semibold text-gray-600 mb-2">
                  Sources:
                </p>
                <ul className="space-y-2">
                  {sources.map((source, index) => (
                    <li key={index} className="text-sm">
                      <a 
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[#a984b2] hover:underline"
                      >
                        {source.title}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 