/** @type {import('next').NextConfig} */
const nextConfig = {
  // Outputs a standalone build that includes all dependencies
  output: "standalone",

  // Makes environment variables available to the client-side code
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },

  // Configure image optimization and allowed domains for next/image
  images: {
    unoptimized: true, // Add this to skip image optimization
    remotePatterns: [
      {
        protocol: "https",
        hostname: "*.s3.amazonaws.com",
        pathname: "/**",
      },
      {
        protocol: "https",
        hostname: "product-buddy.s3.amazonaws.com",
        pathname: "/products/**",
      },
      {
        protocol: "https",
        hostname: "*.s3.us-east-1.amazonaws.com",
        pathname: "/**",
      },
    ],
    domains: [
      "product-buddy.s3.amazonaws.com",
      "product-buddy.s3.us-east-1.amazonaws.com",
    ],
  },

  // Use SWC for minification (faster than Terser)
  swcMinify: true,

  // Set timeout for static page generation
  staticPageGenerationTimeout: 0,

  // Configure experimental features
  experimental: {
    serverComponentsExternalPackages: [],
  },

  // Compiler options
  compiler: {
    removeConsole: false, // Keep console.log in production
  },

  // Performance and caching settings
  generateEtags: false, // Disable ETag generation
  compress: true, // Enable gzip compression
  poweredByHeader: false, // Remove X-Powered-By header
  reactStrictMode: true, // Enable React strict mode

  // File configuration
  excludeDefaultMomentLocales: true, // Reduce bundle size
  pageExtensions: ["tsx", "ts", "jsx", "js"], // Valid page extensions

  // Disable static optimization completely
  typescript: {
    ignoreBuildErrors: true,
  },

  distDir: ".next",
  generateBuildId: async () => "build",

  // Add this to ensure proper CSS loading
  webpack: (config) => {
    config.resolve.fallback = { fs: false, path: false };
    return config;
  },
};

module.exports = nextConfig;
