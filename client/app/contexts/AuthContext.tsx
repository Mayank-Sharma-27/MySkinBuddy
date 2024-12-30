"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { getCookieId } from "../utils/cookies";

interface AuthContextType {
  isLoggedIn: boolean;
  userEmail: string | null;
  setLoggedIn: (email: string) => void;
  setLoggedOut: () => void;
  checkAuthStatus: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  const checkAuthStatus = async () => {
    try {
      const cookieId = getCookieId();
      if (!cookieId) return;

      const response = await fetch("http://localhost:8080/auth/verify", {
        headers: {
          "X-Cookie-ID": cookieId,
        },
      });

      const data = await response.json();
      if (data.status === "success") {
        setIsLoggedIn(true);
        setUserEmail(data.user_email);
      }
    } catch (error) {
      console.error("Auth check failed:", error);
    }
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const value = {
    isLoggedIn,
    userEmail,
    setLoggedIn: (email: string) => {
      setIsLoggedIn(true);
      setUserEmail(email);
    },
    setLoggedOut: () => {
      setIsLoggedIn(false);
      setUserEmail(null);
    },
    checkAuthStatus,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
