"use client";

import { useState } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "../contexts/AuthContext";
import { useCookie } from "../utils/CookieProvider";
import { Button } from "./ui/Button";
import { Divider } from "./ui/Divider";
import { API_URL } from "../config";

interface LoginFormProps {
  onSuccess?: () => void;
}

export function LoginForm({ onSuccess }: LoginFormProps) {
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

      const response = await fetch(`${API_URL}/auth/google-login`, {
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

      if (data.status === "success") {
        setLoggedIn(data.user_email, data.user_name);
        if (onSuccess) {
          onSuccess();
        }
      } else {
        setError(data.error || "Login failed");
      }
    } catch (error) {
      console.error("Login error:", error);
      setError("Failed to login. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full space-y-6">
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
          width="100%"
        />
      </div>

      <Divider text="or" />

      <Button
        variant="secondary"
        fullWidth
        onClick={() => (window.location.href = "/about")}
      >
        Learn more about Product Buddy
      </Button>
    </div>
  );
}
