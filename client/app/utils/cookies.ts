import Cookies from 'js-cookie';

export const COOKIE_NAME = 'product-buddy-cookie';

export const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

export const getCookieId = () => {
  // Check if running on client side
  if (typeof window === 'undefined') return null;
  
  let cookieId = localStorage.getItem('skinbuddy_cookie_id');
  
  if (!cookieId) {
    cookieId = generateUUID();
    localStorage.setItem('skinbuddy_cookie_id', cookieId);
  }
  
  return cookieId;
};

export const clearCookieId = (): void => {
  Cookies.remove(COOKIE_NAME);
}; 