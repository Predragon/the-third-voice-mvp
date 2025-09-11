import { NextConfig } from 'next';
import withPWA from 'next-pwa';
import runtimeCaching from 'next-pwa/cache';

const isDev = process.env.NODE_ENV === 'development';

const nextConfig: NextConfig = withPWA({
  dest: 'public',
  disable: isDev,
  register: true,
  skipWaiting: true,
  buildExcludes: [/middleware-manifest\.json$/],
  runtimeCaching: [
    {
      urlPattern: /^https:\/\/api\.thethirdvoice\.ai\/.*/i,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'api-cache',
        expiration: {
          maxEntries: 32,
          maxAgeSeconds: 24 * 60 * 60, // 24 hours
        },
      },
    },
    ...runtimeCaching, // default PWA runtime cache for static assets
  ],

  // Next.js core config
  output: 'export',
  trailingSlash: true,
  reactStrictMode: true,
  poweredByHeader: false,
  compress: true,
  images: { unoptimized: true },

  env: {
    NEXT_PUBLIC_API_URL: 'https://api.thethirdvoice.ai',
  },

  eslint: {
    ignoreDuringBuilds: true,
  },

  webpack: (config, { isServer }) => {
    // Cloudflare Pages optimization
    if (process.env.CF_PAGES) {
      config.cache = false;
    }

    if (!isServer) {
      config.resolve = config.resolve || {};
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }

    return config;
  },
});

export default nextConfig;
