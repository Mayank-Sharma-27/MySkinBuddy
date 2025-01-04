import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "./contexts/AuthContext";
import { CookieProvider } from "./utils/CookieProvider";
import { MessageLimitProvider } from "./contexts/MessageLimitContext";
import { GoogleOAuthProvider } from "@react-oauth/google";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MySkinBuddy",
  description: "Your AI-powered skincare companion",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <GoogleOAuthProvider
          clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ""}
        >
          <CookieProvider>
            <AuthProvider>
              <MessageLimitProvider>{children}</MessageLimitProvider>
            </AuthProvider>
          </CookieProvider>
        </GoogleOAuthProvider>
      </body>
    </html>
  );
}
