/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
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
  // Disable static generation
  staticPageGenerationTimeout: 0,
  experimental: {
    serverComponentsExternalPackages: [],
  },
  // Disable static optimization
  compiler: {
    removeConsole: false,
  },
  // Cache settings
  generateEtags: false,
  compress: true,
  poweredByHeader: false,
  reactStrictMode: true,
};

module.exports = nextConfig;
