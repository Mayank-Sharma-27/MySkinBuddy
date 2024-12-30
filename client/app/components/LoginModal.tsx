"use client";

import { useEffect } from "react";
import { LoginForm } from "./LoginForm";
import { Button } from "./ui/Button";
import { createPortal } from "react-dom";

interface LoginModalProps {
  onClose: () => void;
  message?: string;
}

export default function LoginModal({ onClose, message }: LoginModalProps) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [onClose]);

  const modalContent = (
    <div
      className="fixed inset-0 flex items-center justify-center z-[100]"
      aria-modal="true"
      role="dialog"
    >
      <div
        className="fixed inset-0 bg-black/30 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        className="relative w-full max-w-md bg-white rounded-xl p-8 shadow-xl mx-4 transform transition-all"
        onClick={(e) => e.stopPropagation()}
        style={{ maxHeight: "90vh", overflowY: "auto" }}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
          aria-label="Close modal"
        >
          ×
        </button>

        <div className="mb-8 text-center">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent mb-2">
            Welcome Back
          </h2>
          {message && <p className="text-gray-600">{message}</p>}
        </div>

        <LoginForm onSuccess={onClose} />

        <div className="mt-6">
          <Button variant="outline" fullWidth onClick={onClose}>
            Continue without signing in
          </Button>
        </div>
      </div>
    </div>
  );

  return typeof window === "object"
    ? createPortal(modalContent, document.body)
    : null;
}
