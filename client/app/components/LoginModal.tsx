"use client";

import { LoginForm } from './LoginForm';

interface LoginModalProps {
  onClose: () => void;
  message: string;
}

export default function LoginModal({ onClose, message }: LoginModalProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div 
        className="bg-white rounded-lg p-6 max-w-md w-full relative"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-6 text-center">
          <p className="text-gray-600">{message}</p>
        </div>

        <LoginForm />

        <button
          onClick={onClose}
          className="mt-4 w-full text-gray-500 hover:text-gray-700 text-sm"
        >
          Continue without signing in
        </button>
      </div>
    </div>
  );
}
