"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
  ReactNode,
} from "react";
import { getCookieId } from "../utils/cookies";
import { API_URL } from "../config";
import { useAuth } from "./AuthContext";

interface MessageLimitContextType {
  showLoginPrompt: boolean;
  checkMessageLimit: () => Promise<boolean>;
  resetLoginPrompt: () => void;
}

const MessageLimitContext = createContext<MessageLimitContextType | undefined>(
  undefined
);

export function MessageLimitProvider({ children }: { children: ReactNode }) {
  const [showLoginPrompt, setShowLoginPrompt] = useState(false);
  const { isLoggedIn } = useAuth();
  const lastCheckRef = useRef<number>(0);
  const checkTimeoutRef = useRef<NodeJS.Timeout>();
  const userDismissedRef = useRef<boolean>(false);

  const checkMessageLimit = useCallback(async () => {
    try {
      const cookieId = getCookieId();
      if (!cookieId) return false;

      // If user has dismissed the prompt, don't check for 5 minutes
      if (userDismissedRef.current) {
        return true;
      }

      // Prevent checking more often than every 30 seconds
      const now = Date.now();
      if (now - lastCheckRef.current < 30000) {
        return !showLoginPrompt;
      }
      lastCheckRef.current = now;

      const response = await fetch(`${API_URL}/check-message-limit`, {
        headers: {
          "X-Cookie-ID": cookieId,
        },
      });

      const data = await response.json();
      if (response.status === 403 && data.requires_login) {
        setShowLoginPrompt(true);
        return false;
      }
      return true;
    } catch (error) {
      return false;
    }
  }, [showLoginPrompt]);

  // Check message limit on initial load
  useEffect(() => {
    if (!isLoggedIn && !userDismissedRef.current) {
      checkMessageLimit();
    }
  }, [isLoggedIn, checkMessageLimit]);

  // Check message limit every 5 minutes
  useEffect(() => {
    if (!isLoggedIn) {
      // Clear any existing timeout
      if (checkTimeoutRef.current) {
        clearTimeout(checkTimeoutRef.current);
      }

      checkTimeoutRef.current = setTimeout(() => {
        userDismissedRef.current = false; // Reset the dismissed state after 5 minutes
        checkMessageLimit();
      }, 5 * 60 * 1000);

      return () => {
        if (checkTimeoutRef.current) {
          clearTimeout(checkTimeoutRef.current);
        }
      };
    }
  }, [isLoggedIn, checkMessageLimit]);

  const resetLoginPrompt = useCallback(() => {
    setShowLoginPrompt(false);
    userDismissedRef.current = true; // Mark as dismissed
  }, []);

  const value = {
    showLoginPrompt,
    checkMessageLimit,
    resetLoginPrompt,
  };

  return (
    <MessageLimitContext.Provider value={value}>
      {children}
    </MessageLimitContext.Provider>
  );
}

export const useMessageLimit = () => {
  const context = useContext(MessageLimitContext);
  if (context === undefined) {
    throw new Error(
      "useMessageLimit must be used within a MessageLimitProvider"
    );
  }
  return context;
};
