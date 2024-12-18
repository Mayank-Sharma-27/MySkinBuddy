"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";

export function LoginForm() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleGoogleLogin = async () => {
    console.log("Google login clicked");
    // Will implement later
  };

  const handleFacebookLogin = async () => {
    console.log("Facebook login clicked");
    // Will implement later
  };

  return (
    <div className="w-full max-w-md space-y-6">
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>
      )}

      <button
        onClick={handleGoogleLogin}
        disabled={loading}
        className="w-full flex items-center justify-center gap-3 px-4 py-3 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-200 transition-colors"
      >
        <Image src="/google.svg" alt="Google" width={20} height={20} />
        <span>Continue with Google</span>
      </button>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-300"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-white text-gray-500">or</span>
        </div>
      </div>

      <button
        onClick={handleFacebookLogin}
        disabled={loading}
        className="w-full flex items-center justify-center gap-3 px-4 py-3 text-white bg-[#1877F2] rounded-lg hover:bg-[#1864D9] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#1877F2] transition-colors"
      >
        <Image src="/facebook.svg" alt="Facebook" width={20} height={20} />
        <span>Continue with Facebook</span>
      </button>

      <button
        onClick={() => window.open("https://productbuddy.xyz", "_blank")}
        className="w-full px-4 py-3 text-sm text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-200 transition-colors"
      >
        Learn more about Product Buddy
      </button>
    </div>
  );
}
