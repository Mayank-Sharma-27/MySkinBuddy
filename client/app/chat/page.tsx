"use client";
import { useSearchParams } from "next/navigation";
import { ChatWindow } from "../components/ChatWindow";
import { Navbar } from "../components/Navbar";

export default function ChatPage() {
  const searchParams = useSearchParams();
  const chatId = searchParams.get("chatId");
  const productName = searchParams.get("product");
  const brandName = searchParams.get("brand");
  const initialMessage = searchParams.get("message");
  const imageUrl = searchParams.get("imageUrl");

  if (!chatId || !productName || !brandName || !initialMessage || !imageUrl) {
    return <div>Missing required parameters</div>;
  }

  return (
    <div className="min-h-screen bg-[#faf4f4]">
      <Navbar />
      <div className="h-[calc(100vh-64px)]">
        {" "}
        {/* Adjust 64px based on your navbar height */}
        <ChatWindow
          chatId={chatId}
          initialMessage={decodeURIComponent(initialMessage)}
          productName={decodeURIComponent(productName)}
          brandName={decodeURIComponent(brandName)}
          fullPage={true}
          imageUrl={decodeURIComponent(imageUrl)}
        />
      </div>
    </div>
  );
}
