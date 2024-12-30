"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "../contexts/AuthContext";
import { useCookie } from "../utils/CookieProvider";

interface LoginFormProps {
  onSuccess?: () => void;
}

export function LoginForm({ onSuccess }: LoginFormProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setLoggedIn } = useAuth();
  const cookieId = useCookie();

  const handleGoogleLogin = async (credentialResponse: any) => {
    try {
      setLoading(true);
      setError(null);

      if (!cookieId) {
        setError("Session error. Please refresh the page.");
        return;
      }

      if (!credentialResponse?.credential) {
        setError("Failed to get Google credentials");
        return;
      }

      console.log("Sending token to backend...");
      const response = await fetch("http://localhost:8080/auth/google-login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Cookie-ID": cookieId,
        },
        body: JSON.stringify({
          token: credentialResponse.credential,
        }),
      });

      const data = await response.json();
      console.log("Backend response:", data);

      if (data.status === "success") {
        setLoggedIn(data.user_email);
        if (onSuccess) {
          onSuccess();
        }
        router.refresh();
      } else {
        setError(data.error || "Login failed");
        console.error("Login error details:", data);
      }
    } catch (error) {
      console.error("Login error:", error);
      setError("Failed to login. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md space-y-6">
      {error && (
        <div className="p-3 text-sm text-red-600 bg-red-50 rounded-lg">
          {error}
        </div>
      )}

      <div className="w-full flex justify-center">
        <GoogleLogin
          onSuccess={handleGoogleLogin}
          onError={() => {
            setError("Google Login Failed");
          }}
          useOneTap
          theme="outline"
          size="large"
          text="continue_with"
          shape="rectangular"
          scope="email profile"
        />
      </div>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-300"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-white text-gray-500">or</span>
        </div>
      </div>

      <button
        onClick={() => window.open("https://productbuddy.xyz", "_blank")}
        className="w-full px-4 py-3 text-sm text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-200 transition-colors"
      >
        Learn more about Product Buddy
      </button>
    </div>
  );
}
