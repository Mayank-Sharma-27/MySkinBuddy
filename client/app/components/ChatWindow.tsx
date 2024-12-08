'use client';
import { useState, useRef, useEffect } from 'react';
import { getCookieId } from '../utils/cookies';

interface Message {
  content: string;
  isBot: boolean;
}

interface ChatWindowProps {
  chatId: string;
  initialMessage: string;
  productName: string;
  brandName: string;
  imageUrl: string;
  fullPage?: boolean;
  onClose?: () => void;
}

export function ChatWindow({ 
  chatId, 
  initialMessage, 
  productName, 
  brandName, 
  imageUrl, 
  fullPage = false,
  onClose 
}: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([
    { content: initialMessage, isBot: true }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const messageContainerRef = useRef<null | HTMLDivElement>(null);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage;
    setInputMessage('');
    setMessages(prev => [...prev, { content: userMessage, isBot: false }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8080/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Cookie-ID': getCookieId()
        },
        body: JSON.stringify({
          chat_id: chatId,
          message: userMessage,
          product_name: productName,
          brand_name: brandName,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      // Add initial bot message
      setMessages(prev => [...prev, { content: '', isBot: true }]);

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response stream available');

      let accumulatedContent = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          // Final update with accumulated content
          setMessages(prev => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1].content = accumulatedContent;
            return newMessages;
          });
          break;
        }

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const content = line.slice(6);
            accumulatedContent += content;
            
            // Update message with accumulated content
            setMessages(prev => {
              const newMessages = [...prev];
              newMessages[newMessages.length - 1].content = accumulatedContent;
              return newMessages;
            });
          }
        }
      }

    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        content: 'Sorry, I encountered an error. Please try again.',
        isBot: true 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-scroll function
  const scrollToBottom = () => {
    if (messageContainerRef.current) {
      const { scrollHeight, clientHeight } = messageContainerRef.current;
      messageContainerRef.current.scrollTo({
        top: scrollHeight - clientHeight,
        behavior: 'smooth'
      });
    }
  };

  // Scroll on new messages or content updates
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className={fullPage ? "h-full" : "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4"}>
      <div className={fullPage ? "bg-white w-full h-full flex flex-col" : "bg-white rounded-lg w-full max-w-2xl h-[600px] flex flex-col"}>
        {/* Header */}
        <div className="p-4 border-b flex items-center justify-between bg-[#faf4f4]">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-lg overflow-hidden flex-shrink-0">
              <img 
                src={imageUrl}
                alt={productName}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.currentTarget.src = '/placeholder-product.png';
                }}
              />
            </div>
            <div>
              <h3 className="font-semibold text-[#a984b2]">{productName}</h3>
              <p className="text-sm text-gray-600">{brandName}</p>
            </div>
          </div>
          {!fullPage && onClose && (
            <button 
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ×
            </button>
          )}
        </div>

        {/* Messages */}
        <div 
          ref={messageContainerRef}
          className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth"
        >
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.isBot ? 'justify-start' : 'justify-end'}`}
            >
              <div
                className={`max-w-[80%] p-3 rounded-lg ${
                  message.isBot
                    ? 'bg-[#faf4f4] text-gray-800'
                    : 'bg-[#a984b2] text-white'
                }`}
              >
                {message.content}
              </div>
            </div>
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