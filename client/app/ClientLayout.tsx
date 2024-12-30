"use client";

import { GoogleOAuthProvider } from "@react-oauth/google";
import { AuthProvider } from "./contexts/AuthContext";
import { CookieProvider } from "./utils/CookieProvider";

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  if (!GOOGLE_CLIENT_ID) {
    console.error("GOOGLE_CLIENT_ID is not set");
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
