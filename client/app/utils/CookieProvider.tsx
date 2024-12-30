"use client";
import { createContext, useContext, useEffect, useState } from "react";
import { getCookieId } from "./cookies";

const CookieContext = createContext<string | null>(null);

export function CookieProvider({ children }: { children: React.ReactNode }) {
  const [cookieId, setCookieId] = useState<string | null>(null);

  useEffect(() => {
    // Initialize cookie on first visit
    const id = getCookieId();
    setCookieId(id);
  }, []);

  return (
    <CookieContext.Provider value={cookieId}>{children}</CookieContext.Provider>
  );
}

export const useCookie = () => {
  const context = useContext(CookieContext);
  if (context === undefined) {
    throw new Error("useCookie must be used within a CookieProvider");
  }
  return context;
};
