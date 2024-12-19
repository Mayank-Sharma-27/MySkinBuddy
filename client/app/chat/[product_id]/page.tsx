'use client';

import { useSearchParams } from 'next/navigation';
import { ChatWindow } from '../../components/ChatWindow';
import { Navbar } from '../../components/Navbar';

interface PageProps {
  params: {
    product_id: string;
  };
}

export default function ChatPage({ params }: PageProps) {
  const { product_id } = params;
  const searchParams = useSearchParams();
  const chat_id = searchParams.get('chat_id');
  const initial_message = searchParams.get('message');

  if (!chat_id) {
    return <div>Missing required parameters</div>;
  }

  return (
    <div className="min-h-screen bg-[#faf4f4]">
      <Navbar />
      <div className="h-[calc(100vh-64px)]">
        <ChatWindow
          chatId={chat_id}
          productId={product_id}
          initialMessage={decodeURIComponent(initial_message)}
          fullPage={true}
        />
      </div>
    </div>
  );
} 