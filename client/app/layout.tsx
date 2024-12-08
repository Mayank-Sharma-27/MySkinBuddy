import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { CookieProvider } from "./utils/CookieProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MySkinBuddy",
  description: "Your intelligent skincare assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <script
          src="https://accounts.google.com/gsi/client"
          async
          defer
        ></script>
      </head>
      <body className={inter.className}>
        <CookieProvider>{children}</CookieProvider>
      </body>
    </html>
  );
}
