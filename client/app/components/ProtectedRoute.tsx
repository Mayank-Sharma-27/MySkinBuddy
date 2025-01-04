"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../contexts/AuthContext";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const { isLoggedIn, checkAuthStatus } = useAuth();
  const [hasCheckedAuth, setHasCheckedAuth] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      await checkAuthStatus();
      setHasCheckedAuth(true);
    };
    checkAuth();
  }, [checkAuthStatus]);

  useEffect(() => {
    if (hasCheckedAuth && !isLoggedIn) {
      router.replace("/login");
    }
  }, [isLoggedIn, router, hasCheckedAuth]);

  // Show loading state while checking auth
  if (!hasCheckedAuth) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        Loading...
      </div>
    );
  }

  // Show nothing briefly while redirecting
  if (!isLoggedIn) {
    return null;
  }

  return <>{children}</>;
}
