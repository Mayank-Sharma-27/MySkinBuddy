"use client";

import { AuthProvider } from "./contexts/AuthContext";
import { CookieProvider } from "./utils/CookieProvider";
import { GoogleOAuthProvider } from "@react-oauth/google";

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

export function Providers({ children }: { children: React.ReactNode }) {
  if (!GOOGLE_CLIENT_ID) {
    console.error("NEXT_PUBLIC_GOOGLE_CLIENT_ID is not set");
    return <div>Configuration Error</div>;
  }

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <CookieProvider>
        <AuthProvider>{children}</AuthProvider>
      </CookieProvider>
    </GoogleOAuthProvider>
  );
}
