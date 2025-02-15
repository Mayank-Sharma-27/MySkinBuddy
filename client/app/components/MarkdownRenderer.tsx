import React from "react";

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({
  content,
}) => {
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

  const formatContent = (text: string) => {
    // Clean up extra newlines and remove citations
    const cleanText = text
      .replace(/\n{3,}/g, "\n\n")
      .replace(/\[\d+\](?:\[\d+\])*/g, "") // Remove citation references
      .trim();

    // Split by lines to handle headings and content separately
    const parts = cleanText.split(
      /(\#{1,3}\s+[^\n]+\n|\d+\.\s+[^\n]+\n|-\s+[^\n]+\n)/g
    );

    return parts.map((part, index) => {
      // Handle markdown headings (## or ###)
      const markdownHeadingMatch = part.match(/^(#{1,3})\s+([^\n]+)/);
      if (markdownHeadingMatch) {
        const [_, hashes, content] = markdownHeadingMatch;
        const level = hashes.length;
        const isMainTitle = level === 2;
        return (
          <h1
            key={index}
            className={`${
              isMainTitle
                ? "text-xl font-semibold text-purple-600 mt-3 mb-4"
                : "text-lg font-semibold text-purple-600 mt-3 mb-2"
            }`}
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
          <div key={index} className="ml-4 mb-1.5">
            {formatBoldText(content.trim())}
          </div>
        );
      }

      // Handle bullet points (- Text)
      const bulletMatch = part.match(/^-\s+([^\n]+)/);
      if (bulletMatch) {
        const [_, content] = bulletMatch;
        return (
          <div key={index} className="ml-4 mb-1.5">
            • {formatBoldText(content.trim())}
          </div>
        );
      }

      // Handle regular text with bold formatting
      if (part.trim()) {
        return (
          <div key={index} className="mb-1.5">
            {formatBoldText(part.trim())}
          </div>
        );
      }

      return null;
    });
  };

  return (
    <div className="markdown-content space-y-0">{formatContent(content)}</div>
  );
};
