import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "./contexts/AuthContext";
import { CookieProvider } from "./utils/CookieProvider";
import { MessageLimitProvider } from "./contexts/MessageLimitContext";
import { GoogleOAuthProvider } from "@react-oauth/google";

const inter = Inter({ subsets: ["latin"] });

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#6366f1",
};

export const metadata: Metadata = {
  title: {
    template: "%s | MyGlowPal",
    default: "MyGlowPal - Your AI Skincare Assistant",
  },
  description:
    "Get personalized skincare recommendations and product analysis with MyGlowPal AI assistant.",
  applicationName: "MyGlowPal",
  authors: [{ name: "MyGlowPal Team" }],
  keywords: ["skincare", "AI", "beauty", "product analysis", "recommendations"],
  creator: "MyGlowPal",
  publisher: "MyGlowPal",
  formatDetection: {
    telephone: false,
    email: false,
    address: false,
  },
  metadataBase: new URL("https://myglowpal.com"),
  openGraph: {
    type: "website",
    siteName: "MyGlowPal",
    title: "MyGlowPal - Your AI Skincare Assistant",
    description:
      "Get personalized skincare recommendations and product analysis with MyGlowPal AI assistant.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "MyGlowPal - Your AI Skincare Assistant",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    site: "@myglowpal",
    creator: "@myglowpal",
    title: "MyGlowPal - Your AI Skincare Assistant",
    description:
      "Get personalized skincare recommendations and product analysis with MyGlowPal AI assistant.",
    images: ["/twitter-image.png"],
  },
  viewport: {
    width: "device-width",
    initialScale: 1,
    maximumScale: 1,
    userScalable: false,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  icons: {
    icon: [
      { url: "/favicon.ico" },
      { url: "/icon.png", type: "image/png" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
    ],
    apple: [{ url: "/apple-icon.png", sizes: "180x180", type: "image/png" }],
    other: [
      {
        rel: "mask-icon",
        url: "/safari-pinned-tab.svg",
      },
    ],
  },
  manifest: "/manifest.json",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#000000" },
  ],
};

// Force dynamic rendering at the root layout
export const dynamic = "force-dynamic";
export const revalidate = 0;
export const fetchCache = "force-no-store";
export const runtime = "nodejs";
export const preferredRegion = "auto";
export const maxDuration = 60;

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
