/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'product-buddy.s3.amazonaws.com',
        port: '',
        pathname: '/products/**',
      },
    ],
  },
};

export default nextConfig;
