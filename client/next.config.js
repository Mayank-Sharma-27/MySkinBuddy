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
    domains: ["product-buddy.s3.amazonaws.com"],
    remotePatterns: [
      {
        protocol: "https",
        hostname: "product-buddy.s3.amazonaws.com",
        pathname: "/products/**",
      },
    ],
  },

  // Use SWC for minification (faster than Terser)
  swcMinify: true,

  // Set timeout for static page generation
  staticPageGenerationTimeout: 0,

  // Configure experimental features
  experimental: {
    serverComponentsExternalPackages: [],
    optimizeFonts: false,
    optimizeImages: false,
    workerThreads: false,
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
};

module.exports = nextConfig;
