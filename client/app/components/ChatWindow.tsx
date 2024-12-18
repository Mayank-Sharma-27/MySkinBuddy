'use client';
import { useState, useRef, useEffect } from 'react';
import { getCookieId } from '../utils/cookies';
import { ChatMessage } from './ChatMessage';

interface Message {
  content: string;
  isBot: boolean;
  sources?: Array<{
    title: string;
    url: string;
  }>;
}

interface StreamResponse {
  content: string;
  sources: Array<{
    title: string;
    url: string;
  }>;
}

interface StreamChunk {
  content: string;
  sources: Array<{url: string; title: string}>;
  type?: 'final';
}

export function ChatWindow({ chatId, initialMessage, productName, brandName, imageUrl, fullPage = false, onClose }: {
  chatId: string;
  initialMessage: string;
  productName: string;
  brandName: string;
  imageUrl: string;
  fullPage?: boolean;
  onClose?: () => void;
}) {
  const [messages, setMessages] = useState<Message[]>([
    { content: initialMessage, isBot: true }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSendMessage = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage;
    setInputMessage('');
    setMessages(prev => [...prev, { content: userMessage, isBot: false }]);
    setIsLoading(true);

    try {
      setMessages(prev => [...prev, { content: '', isBot: true, sources: [] }]);

      const response = await fetch('http://localhost:8080/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Cookie-ID': getCookieId(),
        },
        body: JSON.stringify({
          chat_id: chatId,
          message: userMessage,
        }),
      });

      if (!response.ok) throw new Error('Failed to send message');

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response stream available');

      const decoder = new TextDecoder();
      let buffer = '';
      let accumulatedContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const messages = buffer.split('\n\n');
        buffer = messages.pop() || '';

        for (const message of messages) {
          if (message.startsWith('data: ')) {
            try {
              const data = JSON.parse(message.slice(6));
              console.log('Received chunk:', data);

              if (data.type === 'final') {
                setMessages(prev => {
                  const newMessages = [...prev];
                  newMessages[newMessages.length - 1] = {
                    content: accumulatedContent,
                    isBot: true,
                    sources: data.sources?.map(url => ({
                      title: new URL(url).hostname,
                      url: url
                    }))
                  };
                  return newMessages;
                });
              } else {
                if (data.content?.trim()) {
                  accumulatedContent += data.content;
                  setMessages(prev => {
                    const newMessages = [...prev];
                    newMessages[newMessages.length - 1] = {
                      ...newMessages[newMessages.length - 1],
                      content: accumulatedContent
                    };
                    return newMessages;
                  });
                }
              }
            } catch (error) {
              console.error('Error parsing message:', error);
            }
          }
        }
      }

    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        content: 'Sorry, I encountered an error. Please try again.',
        isBot: true,
        sources: []
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-scroll effect
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const formatContent = (content: string) => {
    // Check if content is a comma-separated list of URLs
    if (content.includes('http') && content.includes(',')) {
      const links = content.split(',').map(url => url.trim());
      return (
        <div className="flex flex-col gap-2">
          {links.map((url, index) => (
            <a 
              key={index}
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 hover:text-blue-700 underline break-all"
            >
              {new URL(url).hostname}
            </a>
          ))}
        </div>
      );
    }
    
    // Regular content
    return <span>{content}</span>;
  };

  return (
    <div className={fullPage ? "h-full" : "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4"}>
      <div className={fullPage ? "bg-white w-full h-full flex flex-col" : "bg-white rounded-lg w-full max-w-2xl h-[600px] flex flex-col"}>
        {/* Header */}
        <div className="p-4 border-b flex items-center justify-between bg-[#faf4f4]">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-lg overflow-hidden">
              <img 
                src={imageUrl} 
                alt={productName}
                className="w-full h-full object-cover"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.src = '/placeholder-product.png';
                }}
              />
            </div>
            <div>
              <h3 className="font-semibold text-[#a984b2]">{productName}</h3>
              <p className="text-sm text-gray-600">{brandName}</p>
            </div>
          </div>
          {!fullPage && onClose && (
            <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
              ×
            </button>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <ChatMessage
              key={index}
              message={message.content}
              isUser={!message.isBot}
              sources={message.sources}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSendMessage} className="p-4 border-t">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask about this product..."
              className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#a984b2]"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !inputMessage.trim()}
              className={`px-4 py-2 rounded-lg ${
                isLoading || !inputMessage.trim()
                  ? 'bg-gray-300 cursor-not-allowed'
                  : 'bg-[#a984b2] hover:bg-[#8e6d97] text-white'
              }`}
            >
              {isLoading ? '...' : 'Send'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 