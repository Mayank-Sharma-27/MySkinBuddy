"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { LoginForm } from "../components/LoginForm";
import { useAuth } from "../contexts/AuthContext";

export default function LoginPage() {
  const router = useRouter();
  const { isLoggedIn, checkAuthStatus } = useAuth();

  useEffect(() => {
    // Check auth status when component mounts
    checkAuthStatus();
  }, [checkAuthStatus]);

  useEffect(() => {
    // Redirect to home if logged in
    if (isLoggedIn) {
      router.replace("/");
    }
  }, [isLoggedIn, router]);

  // Show loading or nothing while checking auth status
  if (isLoggedIn) {
    return null;
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-8 text-purple-600">Welcome Back</h1>
      <LoginForm />
    </main>
  );
}
