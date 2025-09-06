/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export', // Required for Cloudflare Pages (static site)
  trailingSlash: true, // Ensures consistent URLs
  images: {
    unoptimized: true, // Disable Next.js image opt for Cloudflare
  },
  // PWA support (if using next-pwa)
  pwa: {
    dest: 'public',
    disable: process.env.NODE_ENV === 'development',
  },
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NODE_ENV === 'development'
        ? 'https://api.thethirdvoice.ai' // Or dev-api if separate
        : 'https://api.thethirdvoice.ai',
  },
};

export default nextConfig;