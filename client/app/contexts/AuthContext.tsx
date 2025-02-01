"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { getCookieId } from "../utils/cookies";
import { API_URL } from "../config";

interface AuthContextType {
  isLoggedIn: boolean;
  userEmail: string | null;
  userName: string | null;
  setLoggedIn: (email: string, name: string) => void;
  setLoggedOut: () => void;
  checkAuthStatus: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [userName, setUserName] = useState<string | null>(null);

  const checkAuthStatus = async () => {
    try {
      const cookieId = getCookieId();
      if (!cookieId) return;

      const response = await fetch(`${API_URL}/auth/verify`, {
        headers: {
          "X-Cookie-ID": cookieId,
        },
      });

      const data = await response.json();
      if (data.status === "success") {
        setIsLoggedIn(true);
        setUserEmail(data.user_email);
        setUserName(data.user_name);
      }
    } catch (error) {
      // Remove console.error("Auth check failed:", error);
    }
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const value = {
    isLoggedIn,
    userEmail,
    userName,
    setLoggedIn: (email: string, name: string) => {
      setIsLoggedIn(true);
      setUserEmail(email);
      setUserName(name);
    },
    setLoggedOut: () => {
      setIsLoggedIn(false);
      setUserEmail(null);
      setUserName(null);
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
