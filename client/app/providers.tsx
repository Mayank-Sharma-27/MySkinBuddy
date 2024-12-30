"use client";

import { AuthProvider } from "./contexts/AuthContext";
import { CookieProvider } from "./utils/CookieProvider";
import { GoogleOAuthProvider } from "@react-oauth/google";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <GoogleOAuthProvider clientId="1072133159073-2dg5e4u4qjgsf9s00pgqjv4bdrk8j3mg.apps.googleusercontent.com">
      <CookieProvider>
        <AuthProvider>{children}</AuthProvider>
      </CookieProvider>
    </GoogleOAuthProvider>
  );
}
