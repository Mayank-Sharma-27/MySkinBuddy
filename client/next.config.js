/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  // Enable if you need to access environment variables at build time
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  images: {
    domains: ["product-buddy.s3.amazonaws.com"],
    remotePatterns: [
      {
        protocol: "https",
        hostname: "product-buddy.s3.amazonaws.com",
        pathname: "/products/**",
      },
    ],
  },
  swcMinify: true,
  experimental: {
    // Disable SWC loader to use platform-specific binaries
    swcLoader: false,
  },
};

module.exports = nextConfig;
