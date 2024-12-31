export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export const config = {
  apiUrl: API_URL,
  googleClientId: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID,
} as const;
