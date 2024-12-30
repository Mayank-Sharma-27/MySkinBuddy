import Cookies from "js-cookie";

export const COOKIE_NAME = "cookie_id";

export const generateUUID = () => {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
};

export const getCookieId = (): string | null => {
  try {
    // First try to get from document.cookie
    const cookies = document.cookie.split(";");
    let cookieId = cookies
      .find((cookie) => cookie.trim().startsWith(`${COOKIE_NAME}=`))
      ?.split("=")[1];

    // If no cookie exists, create one
    if (!cookieId) {
      cookieId = generateUUID();
      document.cookie = `${COOKIE_NAME}=${cookieId}; path=/; max-age=${
        365 * 24 * 60 * 60
      }; SameSite=Strict`;
    }

    return cookieId;
  } catch (error) {
    console.error("Error managing cookie:", error);
    return null;
  }
};

export const clearCookieId = (): void => {
  document.cookie = `${COOKIE_NAME}=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT`;
};
