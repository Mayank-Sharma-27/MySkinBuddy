"use client";

import Link from "next/link";
import { useAuth } from "../contexts/AuthContext";
import { Container } from "./ui/Container";
import { Button } from "./ui/Button";
import { useState, useCallback } from "react";
import dynamic from "next/dynamic";
import { useCookie } from "../utils/CookieProvider";
import { API_URL } from "../config";

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

      const response = await fetch(`${API_URL}/auth/logout`, {
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
                    href="/profile"
                    className="text-sm font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent hover:opacity-80 transition-opacity"
                  >
                    My Profile
                  </Link>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                      {userName}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleLogout}
                      className="font-bold border-primary-600 text-primary-600 hover:bg-primary-50"
                    >
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
