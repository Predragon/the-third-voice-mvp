/** @type {import('next').NextConfig} */
const withPWA = require('next-pwa')({
  dest: 'public',
  disable: process.env.NODE_ENV === 'development',
});

const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: { unoptimized: true },
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NODE_ENV === 'development'
        ? 'https://api.thethirdvoice.ai'
        : 'https://api.thethirdvoice.ai',
  },
};

module.exports = withPWA(nextConfig);
