"use client";

import { ChatMessage as ChatMessageType } from "../types";
import React from "react";
import { MarkdownRenderer } from "./MarkdownRenderer";
import { Citations } from "./Citations";

interface ChatMessageProps {
  message: string | React.ReactNode;
  isUser: boolean;
  timestamp: string;
  isLoading?: boolean;
  isThinkSection?: boolean;
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
  isThinkSection = false,
}: ChatMessageProps) {
  // If message is empty and not loading, don't render anything
  if (!message && !isLoading) return null;

  const formatMessage = (text: string | React.ReactNode) => {
    if (React.isValidElement(text)) {
      return text;
    }

    if (!text || isLoading) {
      return <LoadingDots />;
    }

    if (typeof text !== "string") {
      return text;
    }

    // Split content and citations
    const [content, ...sourcesParts] = text.split(
      "To learn more, you can refer to these sources:"
    );

    return (
      <div className="space-y-2">
        <MarkdownRenderer content={content.trim()} />
        {sourcesParts.length > 0 && (
          <Citations sourcesText={sourcesParts.join("")} />
        )}
      </div>
    );
  };

  const formatContent = (text: string) => {
    // First handle headings and sections
    const parts = text.split(
      /(\#{1,3}\s+[^\n]+\n|\d+\.\s+[^\n]+\n|-\s+[^\n]+\n)/g
    );

    return parts.map((part, index) => {
      // Handle headings (## or ###)
      const headingMatch = part.match(/^(#{1,3})\s+([^\n]+)/);
      if (headingMatch) {
        const [_, hashes, content] = headingMatch;
        const level = hashes.length;
        const className = level === 2 ? "text-xl" : "text-lg";
        return (
          <h1
            key={index}
            className={`${className} font-semibold text-primary-600 mt-4 mb-2`}
          >
            {content.trim()}
          </h1>
        );
      }

      // Handle numbered lists (1. Text)
      const numberedListMatch = part.match(/^\d+\.\s+([^\n]+)/);
      if (numberedListMatch) {
        const [_, content] = numberedListMatch;
        return (
          <div key={index} className="ml-4 mb-2">
            {formatBoldText(content.trim())}
          </div>
        );
      }

      // Handle bullet points (- Text)
      const bulletMatch = part.match(/^-\s+([^\n]+)/);
      if (bulletMatch) {
        const [_, content] = bulletMatch;
        return (
          <div key={index} className="ml-4 mb-2">
            • {formatBoldText(content.trim())}
          </div>
        );
      }

      // Handle regular text with bold formatting
      return formatBoldText(part);
    });
  };

  // Helper function to handle bold text
  const formatBoldText = (text: string) => {
    const boldParts = text.split(/(\*\*[^*]+\*\*)/g);
    return boldParts.map((part, index) => {
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
            : isThinkSection
            ? "bg-gray-100 border border-gray-200 text-gray-600 italic"
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
