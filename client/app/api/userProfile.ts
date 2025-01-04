import { API_URL } from "../config";
import { getCookieId } from "../utils/cookies";

export interface UserProfile {
  skin_type: string;
  skin_issues: string[];
  additional_info: string;
  location: string;
}

export const saveUserProfile = async (
  profile: UserProfile
): Promise<{ status: string; message: string }> => {
  const cookieId = getCookieId();
  const response = await fetch(`${API_URL}/profile`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Cookie-ID": cookieId || "",
    },
    body: JSON.stringify(profile),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to save profile");
  }

  return response.json();
};

export const getUserProfile = async (): Promise<UserProfile> => {
  const cookieId = getCookieId();
  const response = await fetch(`${API_URL}/profile`, {
    method: "GET",
    headers: {
      "X-Cookie-ID": cookieId || "",
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to get profile");
  }

  return response.json();
};
