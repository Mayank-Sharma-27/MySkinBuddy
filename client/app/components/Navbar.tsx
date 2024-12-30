"use client";

import Link from "next/link";
import { useAuth } from "../contexts/AuthContext";
import { Container } from "./ui/Container";
import { Button } from "./ui/Button";
import { useState, useCallback } from "react";
import dynamic from "next/dynamic";
import { useCookie } from "../utils/CookieProvider";

const LoginModal = dynamic(() => import("./LoginModal"), {
  ssr: false,
});

export default function Navbar() {
  const { isLoggedIn, userName, setLoggedOut } = useAuth();
  const [showLoginModal, setShowLoginModal] = useState(false);
  const cookieId = useCookie();

  const handleLogout = async () => {
    try {
      if (!cookieId) return;

      const response = await fetch("http://localhost:8080/auth/logout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Cookie-ID": cookieId,
        },
      });

      const data = await response.json();
      if (data.status === "success") {
        setLoggedOut();
      }
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  const handleOpenModal = useCallback(() => {
    setShowLoginModal(true);
    document.body.style.overflow = "hidden";
  }, []);

  const handleCloseModal = useCallback(() => {
    setShowLoginModal(false);
    document.body.style.overflow = "unset";
  }, []);

  return (
    <>
      <nav className="sticky top-0 z-40 bg-white/80 backdrop-blur-sm border-b border-gray-200/50">
        <Container>
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center space-x-2">
              <h1 className="text-xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                MySkinBuddy
              </h1>
            </Link>

            <div className="flex items-center gap-6">
              {isLoggedIn ? (
                <>
                  <Link
                    href="/chats"
                    className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
                  >
                    My Chats
                  </Link>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-gray-600">{userName}</span>
                    <Button variant="outline" size="sm" onClick={handleLogout}>
                      Sign Out
                    </Button>
                  </div>
                </>
              ) : (
                <Button variant="primary" size="sm" onClick={handleOpenModal}>
                  Sign In
                </Button>
              )}
            </div>
          </div>
        </Container>
      </nav>

      {showLoginModal && (
        <LoginModal
          onClose={handleCloseModal}
          message="Sign in to access all features"
        />
      )}
    </>
  );
}
