export const dynamic = "force-dynamic";
export const dynamicParams = true;
export const revalidate = 0;
export const fetchCache = "force-no-store";
export const runtime = "nodejs";
export const preferredRegion = "auto";

// Your existing config
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000/api";
export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";
