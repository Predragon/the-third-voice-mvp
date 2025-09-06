/** @type {import('next').NextConfig} */
const withPWA = require('next-pwa')({
  dest: 'public', // Outputs service worker and manifest
  disable: process.env.NODE_ENV === 'development', // Disable PWA in dev
});

const nextConfig = {
  output: 'export', // For Cloudflare Pages
  trailingSlash: true,
  images: {
    unoptimized: true, // Cloudflare Pages compatibility
  },
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NODE_ENV === 'development'
        ? 'https://api.thethirdvoice.ai'
        : 'https://api.thethirdvoice.ai',
  },
};

module.exports = withPWA(nextConfig);