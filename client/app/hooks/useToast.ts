"use client";

import { create } from "zustand";

type ToastType = "success" | "error" | "info";

interface ToastState {
  message: string | null;
  type: ToastType;
  showToast: (message: string, type: ToastType) => void;
  hideToast: () => void;
}

export const useToast = create<ToastState>((set) => ({
  message: null,
  type: "info",
  showToast: (message: string, type: ToastType) => {
    set({ message, type });
    setTimeout(() => {
      set({ message: null, type: "info" });
    }, 3000);
  },
  hideToast: () => set({ message: null, type: "info" }),
}));
