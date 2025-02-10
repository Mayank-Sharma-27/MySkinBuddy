"use client";

import { ChatMessage as ChatMessageType } from "../types";
import React from "react";

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
  isLoading = false,
}: ChatMessageProps) {
  // If message is empty and not loading, don't render anything
  if (!message && !isLoading) return null;

  const formatMessage = (text: string | React.ReactNode) => {
    // If message is React component, return it directly
    if (React.isValidElement(text)) {
      return text;
    }

    // If message is empty or loading, return loading dots
    if (!text || isLoading) {
      return <LoadingDots />;
    }

    // Handle string messages
    if (typeof text !== "string") {
      return text;
    }

    // Remove extra spacing and dashes
    const cleanText = text.replace(/\n---\n/g, "").replace(/\n\n+/g, "\n");

    // Split the message into content and sources
    const [content, ...sourcesParts] = cleanText.split(
      "To learn more, you can refer to these sources:"
    );

    if (!sourcesParts.length) {
      return formatContent(content.trim());
    }

    const sourcesText = sourcesParts.join("");
    const sources = sourcesText
      .split("\n")
      .filter((line) => line.trim())
      .map((line) => {
        // Match both formats: numbered list with Read more, or just the name
        const match = line.match(
          /(?:\d+\.\s+)?(.*?)(?:\s*-\s*\[Read more\]\((.*?)\))?$/
        );
        if (match) {
          const [_, name, url] = match;
          return { name: name.trim(), url };
        }
        return null;
      })
      .filter(Boolean);

    // Remove duplicate sources based on name
    const uniqueSources = (sources as (Source | null)[]).reduce<Source[]>(
      (acc, current) => {
        if (!current) return acc;
        const isDuplicate = acc.find((item) => item.name === current.name);
        if (!isDuplicate) {
          acc.push(current);
        }
        return acc;
      },
      []
    );

    return (
      <div className="space-y-2">
        <div>{formatContent(content.trim())}</div>
        {uniqueSources.length > 0 && (
          <div className="border-t border-gray-200 pt-2 mt-3">
            <div className="space-y-2">
              <span className="text-xs font-medium text-gray-600 flex items-center gap-1.5">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-3.5 w-3.5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
                </svg>
                Sources
              </span>
              <div className="flex flex-wrap gap-2">
                {uniqueSources.map((source, index) => (
                  <a
                    key={index}
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs px-3 py-1 rounded-full bg-primary-50 hover:bg-primary-100 text-primary-600 hover:text-primary-700 transition-colors border border-primary-100 flex items-center gap-1"
                  >
                    <span>{source.name}</span>
                    {source.url && (
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-3 w-3"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                        <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                      </svg>
                    )}
                  </a>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const formatContent = (text: string) => {
    // Handle bold text
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        const content = part.slice(2, -2);
        return (
          <span
            key={index}
            className="font-medium bg-primary-100/20 text-primary-700 px-1 rounded"
          >
            {content}
          </span>
        );
      }
      return part;
    });
  };

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      <div
        className={`${
          isLoading ? "min-w-[60px]" : "max-w-[80%]"
        } rounded-2xl py-2 ${
          isUser
            ? "bg-gradient-to-r from-primary-500 to-secondary-500 text-white"
            : "bg-white border border-gray-200 text-gray-800"
        } ${isLoading ? "px-3" : "px-4"}`}
      >
        <div className="space-y-1">
          <div className="whitespace-pre-wrap break-words">
            {formatMessage(message)}
          </div>
          {!isLoading && (
            <div
              className={`text-xs ${
                isUser ? "text-white/70" : "text-gray-500"
              }`}
            >
              {new Date(timestamp).toLocaleTimeString()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
