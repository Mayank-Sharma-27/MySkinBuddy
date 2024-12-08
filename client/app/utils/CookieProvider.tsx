"use client";
import { createContext, useContext, useEffect } from "react";
import { getCookieId } from "./cookies";

const CookieContext = createContext<string | null>(null);

export function CookieProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // Initialize cookie on first visit
    getCookieId();
  }, []);

  return children;
}

export const useCookie = () => {
  const context = useContext(CookieContext);
  if (context === undefined) {
    throw new Error("useCookie must be used within a CookieProvider");
  }
  return context;
};
