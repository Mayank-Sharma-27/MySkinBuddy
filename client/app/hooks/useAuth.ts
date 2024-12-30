"use client";

import { create } from "zustand";

interface AuthState {
  isLoggedIn: boolean;
  userEmail: string | null;
  setLoggedIn: (email: string) => void;
  setLoggedOut: () => void;
}

export const useAuth = create<AuthState>((set) => ({
  isLoggedIn: false,
  userEmail: null,
  setLoggedIn: (email: string) => set({ isLoggedIn: true, userEmail: email }),
  setLoggedOut: () => set({ isLoggedIn: false, userEmail: null }),
}));
